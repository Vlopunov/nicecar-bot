import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session
from app.models import Booking, BookingStatus, User
from app.config import settings
from app.services.notification_service import notify_booking_status

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("admin_confirm_"))
async def admin_confirm_booking(callback: CallbackQuery):
    if callback.from_user.id not in settings.admin_ids_list:
        await callback.answer("Нет доступа")
        return

    booking_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        result = await session.execute(
            select(Booking)
            .where(Booking.id == booking_id)
            .options(selectinload(Booking.user), selectinload(Booking.service))
        )
        booking = result.scalar_one_or_none()

        if not booking:
            await callback.answer("Запись не найдена")
            return

        booking.status = BookingStatus.CONFIRMED
        await session.commit()
        await session.refresh(booking)

        # Notify client
        await notify_booking_status(callback.bot, booking)

    await callback.message.edit_text(
        callback.message.text + "\n\n✅ <b>ПОДТВЕРЖДЕНО</b>",
    )
    await callback.answer("Запись подтверждена!")


@router.callback_query(F.data.startswith("admin_cancel_"))
async def admin_cancel_booking(callback: CallbackQuery):
    if callback.from_user.id not in settings.admin_ids_list:
        await callback.answer("Нет доступа")
        return

    booking_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        result = await session.execute(
            select(Booking)
            .where(Booking.id == booking_id)
            .options(selectinload(Booking.user), selectinload(Booking.service))
        )
        booking = result.scalar_one_or_none()

        if not booking:
            await callback.answer("Запись не найдена")
            return

        booking.status = BookingStatus.CANCELLED
        await session.commit()
        await session.refresh(booking)

        await notify_booking_status(callback.bot, booking)

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ <b>ОТКЛОНЕНО</b>",
    )
    await callback.answer("Запись отклонена")


@router.callback_query(F.data.startswith("admin_details_"))
async def admin_booking_details(callback: CallbackQuery):
    if callback.from_user.id not in settings.admin_ids_list:
        await callback.answer("Нет доступа")
        return

    booking_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        result = await session.execute(
            select(Booking)
            .where(Booking.id == booking_id)
            .options(selectinload(Booking.user), selectinload(Booking.service))
        )
        booking = result.scalar_one_or_none()

    if not booking:
        await callback.answer("Запись не найдена")
        return

    from app.bot.keyboards.webapp import webapp_button
    await callback.message.answer(
        f"📋 Детали записи #{booking.id}\n\n"
        f"Откройте админ-панель для управления:",
        reply_markup=webapp_button("📋 Открыть в админке", f"/admin/bookings?id={booking.id}"),
    )
    await callback.answer()
