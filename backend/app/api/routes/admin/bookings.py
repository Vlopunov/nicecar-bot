from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.api.deps import get_admin_user
from app.models import Booking, BookingStatus, User

router = APIRouter(prefix="/api/admin/bookings", tags=["admin-bookings"])


class BookingUpdate(BaseModel):
    status: str | None = None
    post_id: int | None = None
    price_final: float | None = None
    admin_notes: str | None = None


class ManualBooking(BaseModel):
    user_telegram_id: int | None = None
    client_name: str = ""
    client_phone: str = ""
    service_id: int
    car_brand: str = ""
    car_model: str = ""
    car_class: str | None = None
    date: str
    time: str
    notes: str | None = None


def _booking_detail(b: Booking) -> dict:
    return {
        "id": b.id,
        "user": {
            "id": b.user.id if b.user else None,
            "first_name": b.user.first_name if b.user else "",
            "last_name": b.user.last_name if b.user else "",
            "username": b.user.username if b.user else "",
            "phone": b.user.phone if b.user else "",
            "telegram_id": b.user.telegram_id if b.user else None,
        },
        "service": {"id": b.service.id, "name": b.service.name} if b.service else None,
        "post": {"id": b.post.id, "name": b.post.name} if b.post else None,
        "car_brand": b.car_brand,
        "car_model": b.car_model,
        "car_class": b.car_class,
        "date": b.date.isoformat(),
        "time_start": b.time_start.strftime("%H:%M"),
        "time_end": b.time_end.strftime("%H:%M"),
        "status": b.status.value,
        "price_estimated": float(b.price_estimated) if b.price_estimated else None,
        "price_final": float(b.price_final) if b.price_final else None,
        "notes": b.notes,
        "admin_notes": b.admin_notes,
        "bonus_used": float(b.bonus_used),
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


@router.get("")
async def list_bookings(
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    status: str | None = Query(None),
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    query = select(Booking).options(
        selectinload(Booking.user),
        selectinload(Booking.service),
        selectinload(Booking.post),
    ).order_by(Booking.date.desc(), Booking.time_start)

    conditions = []
    if date_from:
        conditions.append(Booking.date >= date.fromisoformat(date_from))
    if date_to:
        conditions.append(Booking.date <= date.fromisoformat(date_to))
    if status:
        conditions.append(Booking.status == BookingStatus(status))

    if conditions:
        query = query.where(and_(*conditions))

    result = await session.execute(query)
    bookings = result.scalars().all()
    return [_booking_detail(b) for b in bookings]


@router.put("/{booking_id}")
async def update_booking(
    booking_id: int,
    data: BookingUpdate,
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    booking = await session.get(Booking, booking_id)
    if not booking:
        return {"error": "Booking not found"}

    if data.status:
        booking.status = BookingStatus(data.status)
    if data.post_id is not None:
        booking.post_id = data.post_id
    if data.price_final is not None:
        from decimal import Decimal
        booking.price_final = Decimal(str(data.price_final))
    if data.admin_notes is not None:
        booking.admin_notes = data.admin_notes

    await session.commit()
    await session.refresh(booking)

    result = await session.execute(
        select(Booking).where(Booking.id == booking_id).options(
            selectinload(Booking.user),
            selectinload(Booking.service),
            selectinload(Booking.post),
        )
    )
    booking = result.scalar_one()
    return _booking_detail(booking)


@router.post("")
async def create_manual_booking(
    data: ManualBooking,
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    from datetime import time as time_type, timedelta, datetime as dt
    from app.models import Service
    from decimal import Decimal

    service = await session.get(Service, data.service_id)
    if not service:
        return {"error": "Service not found"}

    booking_date = date.fromisoformat(data.date)
    h, m = data.time.split(":")
    booking_time = time_type(int(h), int(m))

    duration_minutes = int(float(service.duration_max_hours) * 60)
    end_dt = dt.combine(booking_date, booking_time) + timedelta(minutes=duration_minutes)

    # Find or create user
    user_id = None
    if data.user_telegram_id:
        result = await session.execute(select(User).where(User.telegram_id == data.user_telegram_id))
        user = result.scalar_one_or_none()
        if user:
            user_id = user.id

    if not user_id:
        user = User(
            telegram_id=0,
            first_name=data.client_name or "Клиент (вручную)",
            phone=data.client_phone,
        )
        session.add(user)
        await session.flush()
        user_id = user.id

    booking = Booking(
        user_id=user_id,
        service_id=data.service_id,
        car_brand=data.car_brand,
        car_model=data.car_model,
        car_class=data.car_class,
        date=booking_date,
        time_start=booking_time,
        time_end=end_dt.time(),
        status=BookingStatus.CONFIRMED,
        notes=data.notes,
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return {"id": booking.id, "status": "created"}
