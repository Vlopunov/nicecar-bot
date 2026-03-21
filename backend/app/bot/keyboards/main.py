from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from app.config import settings


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Услуги и цены"),
                KeyboardButton(text="📅 Записаться"),
            ],
            [
                KeyboardButton(text="📸 Наши работы"),
                KeyboardButton(text="❓ FAQ"),
            ],
            [
                KeyboardButton(text="👤 Личный кабинет"),
                KeyboardButton(text="📞 Связаться"),
            ],
        ],
        resize_keyboard=True,
    )


def webapp_booking_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="📅 Открыть запись",
                web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/booking"),
            )],
            [KeyboardButton(text="◀️ Назад")],
        ],
        resize_keyboard=True,
    )


def webapp_profile_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="👤 Открыть профиль",
                web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/profile"),
            )],
            [KeyboardButton(text="◀️ Назад")],
        ],
        resize_keyboard=True,
    )
