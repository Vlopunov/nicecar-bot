import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.config import settings
from app.models import Booking, User
from app.utils.helpers import format_date, format_time, format_price

logger = logging.getLogger(__name__)


async def notify_new_booking(bot: Bot, booking: Booking, user: User) -> None:
    """Send notification about new booking to admin chat and individual admins."""
    service_name = booking.service.name if booking.service else "N/A"
    price_str = format_price(booking.price_estimated) if booking.price_estimated else "по запросу"

    text = (
        f"🆕 <b>Новая запись!</b>\n\n"
        f"👤 Клиент: {user.first_name} {user.last_name or ''}"
        f"{' (@' + user.username + ')' if user.username else ''}\n"
        f"📱 Тел: {user.phone or 'не указан'}\n"
        f"🚗 {booking.car_brand} {booking.car_model}"
        f"{' (' + booking.car_class + ' класс)' if booking.car_class else ''}\n"
        f"🔧 Услуга: {service_name}\n"
        f"📅 {format_date(booking.date)}, {format_time(booking.time_start)}\n"
        f"💰 От {price_str}\n"
    )

    if booking.notes:
        text += f"\n📝 Комментарий: {booking.notes}\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_{booking.id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_cancel_{booking.id}"),
        ],
        [InlineKeyboardButton(text="📋 Детали", callback_data=f"admin_details_{booking.id}")],
    ])

    try:
        if settings.ADMIN_CHAT_ID:
            await bot.send_message(settings.ADMIN_CHAT_ID, text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Failed to send admin chat notification: {e}")

    for admin_id in settings.admin_ids_list:
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML", reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")


async def notify_booking_status(bot: Bot, booking: Booking) -> None:
    """Notify client about booking status change."""
    status_texts = {
        "confirmed": "✅ Ваша запись подтверждена!",
        "in_progress": "🔧 Ваш автомобиль в работе!",
        "completed": "🎉 Работа завершена! Спасибо, что выбрали NiceCar Center!",
        "cancelled": "❌ Ваша запись отменена.",
    }

    status_text = status_texts.get(booking.status.value, "Статус записи обновлён")
    service_name = booking.service.name if booking.service else "N/A"

    text = (
        f"{status_text}\n\n"
        f"🔧 {service_name}\n"
        f"📅 {format_date(booking.date)}, {format_time(booking.time_start)}\n"
    )

    if booking.status.value == "completed" and booking.price_final:
        text += f"💰 Итого: {format_price(booking.price_final)}\n"

    try:
        user = booking.user
        if user:
            await bot.send_message(user.telegram_id, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to notify user about booking status: {e}")


async def send_reminder(bot: Bot, booking: Booking, hours_before: int) -> None:
    """Send reminder to client before appointment."""
    service_name = booking.service.name if booking.service else ""
    text = (
        f"⏰ Напоминание!\n\n"
        f"Через {hours_before} ч. у вас запись в NiceCar Center:\n"
        f"🔧 {service_name}\n"
        f"📅 {format_date(booking.date)}, {format_time(booking.time_start)}\n"
        f"📍 ул. Петруся Бровки 30, К.11\n\n"
        f"Ждём вас! 🚗"
    )

    try:
        user = booking.user
        if user:
            await bot.send_message(user.telegram_id, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to send reminder: {e}")
