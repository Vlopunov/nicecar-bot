from datetime import date, time
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.api.deps import get_current_user
from app.models import Booking, BookingStatus, User
from app.services.booking_service import create_booking, cancel_booking

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


class BookingCreate(BaseModel):
    service_id: int
    car_brand: str
    car_model: str
    car_class: str | None = None
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    notes: str | None = None
    bonus_used: float = 0


def _booking_to_dict(b: Booking) -> dict:
    return {
        "id": b.id,
        "service": {
            "id": b.service.id,
            "name": b.service.name,
        } if b.service else None,
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
        "bonus_used": float(b.bonus_used),
        "bonus_earned": float(b.bonus_earned),
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


@router.post("")
async def create_booking_endpoint(
    data: BookingCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        booking_date = date.fromisoformat(data.date)
        h, m = data.time.split(":")
        booking_time = time(int(h), int(m))
    except (ValueError, IndexError):
        raise HTTPException(400, "Invalid date or time format")

    try:
        booking = await create_booking(
            session=session,
            user_id=user.id,
            service_id=data.service_id,
            car_brand=data.car_brand,
            car_model=data.car_model,
            car_class=data.car_class,
            booking_date=booking_date,
            booking_time=booking_time,
            notes=data.notes,
            bonus_used=Decimal(str(data.bonus_used)),
        )
        return _booking_to_dict(booking)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/my")
async def get_my_bookings(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Booking)
        .where(Booking.user_id == user.id)
        .options(selectinload(Booking.service))
        .order_by(Booking.date.desc(), Booking.time_start.desc())
    )
    bookings = result.scalars().all()
    return [_booking_to_dict(b) for b in bookings]


@router.put("/{booking_id}/cancel")
async def cancel_booking_endpoint(
    booking_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        booking = await cancel_booking(session, booking_id, user.id)
        return _booking_to_dict(booking)
    except ValueError as e:
        raise HTTPException(400, str(e))
