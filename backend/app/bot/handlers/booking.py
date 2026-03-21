from aiogram import Router, F
from aiogram.types import Message

from app.bot.keyboards.main import webapp_booking_keyboard

router = Router()


@router.message(F.text == "📅 Записаться")
async def start_booking(message: Message):
    text = (
        "📅 <b>Онлайн-запись в NiceCar Center</b>\n\n"
        "Нажмите кнопку ниже, чтобы открыть форму записи.\n"
        "Вы сможете выбрать услугу, дату и удобное время.\n\n"
        "Или напишите нам — мы запишем вас вручную! 📞"
    )
    await message.answer(text, reply_markup=webapp_booking_keyboard())
