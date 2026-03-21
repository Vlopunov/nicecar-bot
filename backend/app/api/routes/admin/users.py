import csv
import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.api.deps import get_admin_user
from app.models import User, Booking

router = APIRouter(prefix="/api/admin/users", tags=["admin-users"])


class UserTagsUpdate(BaseModel):
    tags: str | None = None
    notes: str | None = None


@router.get("")
async def list_users(
    search: str | None = Query(None),
    tag: str | None = Query(None),
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    query = select(User).where(User.telegram_id > 0).order_by(User.created_at.desc())

    if search:
        query = query.where(
            User.first_name.ilike(f"%{search}%") |
            User.last_name.ilike(f"%{search}%") |
            User.username.ilike(f"%{search}%") |
            User.phone.ilike(f"%{search}%")
        )
    if tag:
        query = query.where(User.tags.contains(tag))

    result = await session.execute(query)
    users = result.scalars().all()
    return [
        {
            "id": u.id, "telegram_id": u.telegram_id, "username": u.username,
            "first_name": u.first_name, "last_name": u.last_name,
            "phone": u.phone, "bonus_balance": float(u.bonus_balance),
            "total_spent": float(u.total_spent), "visit_count": u.visit_count,
            "tags": u.tags, "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.get("/export")
async def export_users_csv(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.telegram_id > 0).order_by(User.id))
    users = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Telegram ID", "Username", "Имя", "Фамилия", "Телефон",
                     "Бонусы", "Потрачено", "Визиты", "Теги", "Дата регистрации"])
    for u in users:
        writer.writerow([
            u.id, u.telegram_id, u.username or "", u.first_name, u.last_name or "",
            u.phone or "", float(u.bonus_balance), float(u.total_spent), u.visit_count,
            u.tags or "", u.created_at.isoformat() if u.created_at else "",
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=clients.csv"},
    )


@router.get("/{user_id}")
async def get_user_detail(
    user_id: int,
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)
    if not user:
        return {"error": "Not found"}

    bookings_result = await session.execute(
        select(Booking).where(Booking.user_id == user_id)
        .options(selectinload(Booking.service))
        .order_by(Booking.date.desc())
    )
    bookings = bookings_result.scalars().all()

    return {
        "id": user.id, "telegram_id": user.telegram_id, "username": user.username,
        "first_name": user.first_name, "last_name": user.last_name,
        "phone": user.phone, "bonus_balance": float(user.bonus_balance),
        "total_spent": float(user.total_spent), "visit_count": user.visit_count,
        "tags": user.tags, "notes": user.notes,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "bookings": [
            {
                "id": b.id, "service_name": b.service.name if b.service else "",
                "date": b.date.isoformat(), "status": b.status.value,
                "price_final": float(b.price_final) if b.price_final else None,
            }
            for b in bookings
        ],
    }


@router.put("/{user_id}")
async def update_user_admin(
    user_id: int,
    data: UserTagsUpdate,
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)
    if not user:
        return {"error": "Not found"}
    if data.tags is not None:
        user.tags = data.tags
    if data.notes is not None:
        user.notes = data.notes
    await session.commit()
    return {"id": user.id, "tags": user.tags, "notes": user.notes}
