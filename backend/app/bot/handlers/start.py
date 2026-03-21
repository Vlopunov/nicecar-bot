from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy import select

from app.database import async_session
from app.models import User
from app.config import settings
from app.bot.keyboards.main import main_menu_keyboard

router = Router()

WELCOME_TEXT = """🚗 <b>Добро пожаловать в NiceCar Center!</b>

Официальный центр бренда <b>Krytex</b> в Минске.

Детейлинг, защита, оклейка, химчистка и многое другое для вашего автомобиля.

📍 ул. Петруся Бровки 30, К.11
📞 +375 (29) 664-94-87
🕐 ПН-ПТ: 9:00-19:00, СБ: 9:00-18:00

Выберите нужный раздел в меню ниже 👇"""


@router.message(CommandStart())
async def cmd_start(message: Message):
    telegram_id = message.from_user.id

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=telegram_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name or "",
                last_name=message.from_user.last_name,
                is_admin=telegram_id in settings.admin_ids_list,
            )

            # Check referral
            args = message.text.split()
            if len(args) > 1 and args[1].startswith("ref_"):
                try:
                    referrer_id = int(args[1].replace("ref_", ""))
                    ref_result = await session.execute(select(User).where(User.id == referrer_id))
                    referrer = ref_result.scalar_one_or_none()
                    if referrer:
                        user.referrer_id = referrer.id
                except (ValueError, Exception):
                    pass

            session.add(user)
            await session.commit()

    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(F.text == "◀️ Назад")
async def go_back(message: Message):
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard())
