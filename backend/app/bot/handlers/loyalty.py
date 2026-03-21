from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from app.database import async_session
from app.models import User
from app.config import settings
from app.bot.keyboards.main import webapp_profile_keyboard

router = Router()


@router.message(F.text == "👤 Личный кабинет")
async def show_profile(message: Message):
    telegram_id = message.from_user.id

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    if not user:
        await message.answer("Профиль не найден. Нажмите /start для регистрации.")
        return

    bot_info = await message.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user.id}"

    text = (
        f"👤 <b>Личный кабинет</b>\n\n"
        f"Имя: {user.first_name} {user.last_name or ''}\n"
        f"Визиты: {user.visit_count}\n"
        f"💰 Бонусный баланс: {float(user.bonus_balance):.0f} BYN\n"
        f"💳 Потрачено всего: {float(user.total_spent):.0f} BYN\n\n"
        f"🔗 Ваша реферальная ссылка:\n<code>{ref_link}</code>\n"
        f"Пригласите друга и получите {settings.REFERRAL_BONUS} BYN бонусов!\n\n"
        f"Откройте полный профиль в мини-приложении 👇"
    )

    await message.answer(text, reply_markup=webapp_profile_keyboard())


@router.message(F.text == "📞 Связаться")
async def show_contacts(message: Message):
    text = (
        "📞 <b>Контакты NiceCar Center</b>\n\n"
        "📱 Телефон: +375 (29) 664-94-87\n"
        "📍 Адрес: г. Минск, ул. Петруся Бровки 30, К.11\n"
        '🗺 <a href="https://maps.google.com/?q=53.9178,27.5869">Показать на карте</a>\n\n'
        "🕐 Режим работы:\n"
        "  ПН-ПТ: 9:00 — 19:00\n"
        "  СБ: 9:00 — 18:00\n"
        "  ВС: Выходной\n\n"
        "📧 nicecar.center.belarus@gmail.com\n"
        "📸 Instagram: @nicecar.center\n\n"
        "Напишите нам прямо сейчас — ответим в ближайшее время! 💬"
    )

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Позвонить", url="tel:+375296649487")],
        [InlineKeyboardButton(text="💬 Написать менеджеру", callback_data="contact_manager")],
    ])

    await message.answer(text, reply_markup=keyboard, disable_web_page_preview=True)


@router.callback_query(F.data == "contact_manager")
async def contact_manager(callback):
    await callback.message.answer(
        "💬 Напишите ваше сообщение, и менеджер ответит в ближайшее время!"
    )
    await callback.answer()
