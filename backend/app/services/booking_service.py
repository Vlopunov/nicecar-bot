from datetime import date, time, timedelta, datetime
from decimal import Decimal

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Booking, BookingStatus, Service, ServicePrice, User
from app.services.slot_service import get_available_slots


async def create_booking(
    session: AsyncSession,
    user_id: int,
    service_id: int,
    car_brand: str,
    car_model: str,
    car_class: str | None,
    booking_date: date,
    booking_time: time,
    notes: str | None = None,
    bonus_used: Decimal = Decimal(0),
) -> Booking:
    """Create a new booking after validating slot availability."""
    # Get service
    service = await session.get(Service, service_id)
    if not service or not service.is_active:
        raise ValueError("Услуга не найдена или недоступна")

    # Check slot is available
    available = await get_available_slots(session, booking_date, float(service.duration_max_hours))
    if booking_time not in available:
        raise ValueError("Выбранное время недоступно")

    # Calculate end time
    duration_minutes = int(float(service.duration_max_hours) * 60)
    dt_start = datetime.combine(booking_date, booking_time)
    dt_end = dt_start + timedelta(minutes=duration_minutes)

    # Get estimated price
    price_estimated = None
    if car_class:
        price_q = await session.execute(
            select(ServicePrice).where(
                and_(ServicePrice.service_id == service_id, ServicePrice.car_class == car_class)
            )
        )
        price_row = price_q.scalar_one_or_none()
        if price_row:
            price_estimated = price_row.price_from

    if price_estimated is None:
        price_q = await session.execute(
            select(ServicePrice).where(
                and_(ServicePrice.service_id == service_id, ServicePrice.car_class == None)
            )
        )
        price_row = price_q.scalar_one_or_none()
        if price_row:
            price_estimated = price_row.price_from

    booking = Booking(
        user_id=user_id,
        service_id=service_id,
        car_brand=car_brand,
        car_model=car_model,
        car_class=car_class,
        date=booking_date,
        time_start=booking_time,
        time_end=dt_end.time(),
        status=BookingStatus.NEW,
        price_estimated=price_estimated,
        notes=notes,
        bonus_used=bonus_used,
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return booking


async def cancel_booking(session: AsyncSession, booking_id: int, user_id: int) -> Booking:
    """Cancel a booking (only if >24h before appointment)."""
    booking = await session.get(Booking, booking_id)
    if not booking or booking.user_id != user_id:
        raise ValueError("Запись не найдена")

    if booking.status in (BookingStatus.CANCELLED, BookingStatus.COMPLETED):
        raise ValueError("Запись уже отменена или завершена")

    appointment_dt = datetime.combine(booking.date, booking.time_start)
    if datetime.now() > appointment_dt - timedelta(hours=24):
        raise ValueError("Отмена возможна не позднее чем за 24 часа до визита")

    booking.status = BookingStatus.CANCELLED
    await session.commit()
    await session.refresh(booking)
    return booking
