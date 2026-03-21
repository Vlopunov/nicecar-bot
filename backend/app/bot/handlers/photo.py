import logging

from aiogram import Router, F
from aiogram.types import Message

from app.bot.bot import bot
from app.config import settings

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "📸 Наши работы")
async def show_portfolio(message: Message):
    from app.bot.keyboards.webapp import webapp_button
    await message.answer(
        "📸 <b>Наши работы</b>\n\n"
        "Посмотрите примеры наших работ в мини-приложении.\n"
        "Также вы можете отправить фото вашего авто для расчёта стоимости!",
        reply_markup=webapp_button("📸 Открыть портфолио", "/portfolio"),
    )


@router.message(F.photo)
async def receive_photo(message: Message):
    """Client sends a photo — forward to admin chat for calculation."""
    user = message.from_user
    user_info = f"👤 {user.first_name}"
    if user.last_name:
        user_info += f" {user.last_name}"
    if user.username:
        user_info += f" (@{user.username})"

    caption = (
        f"📸 <b>Фото для расчёта</b>\n\n"
        f"{user_info}\n"
        f"ID: {user.id}\n"
    )

    if message.caption:
        caption += f"\n💬 Комментарий: {message.caption}"

    # Forward photo to admin chat
    if settings.ADMIN_CHAT_ID and bot:
        try:
            await bot.send_photo(
                settings.ADMIN_CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=caption,
            )
        except Exception as e:
            logger.error(f"Failed to forward photo to admin chat: {e}")

    await message.answer(
        "✅ Спасибо! Фото получено.\n\n"
        "Менеджер рассчитает стоимость и свяжется с вами "
        "в течение 30 минут (в рабочее время).\n\n"
        "📞 Или позвоните: +375 (29) 664-94-87"
    )
