from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from app.database import async_session
from app.models import FAQ
from app.bot.keyboards.inline import faq_categories_keyboard, faq_questions_keyboard
from app.config import settings

router = Router()


@router.message(F.text == "❓ FAQ")
async def show_faq(message: Message):
    async with async_session() as session:
        result = await session.execute(
            select(FAQ.category).where(FAQ.is_active == True).distinct()
        )
        categories = [row[0] for row in result.all()]

    if not categories:
        await message.answer("FAQ пока не заполнен. Задайте вопрос менеджеру!")
        return

    await message.answer(
        "❓ <b>Часто задаваемые вопросы</b>\n\nВыберите тему:",
        reply_markup=faq_categories_keyboard(categories),
    )


@router.callback_query(F.data == "back_faq")
async def back_to_faq(callback: CallbackQuery):
    async with async_session() as session:
        result = await session.execute(
            select(FAQ.category).where(FAQ.is_active == True).distinct()
        )
        categories = [row[0] for row in result.all()]

    await callback.message.edit_text(
        "❓ <b>Часто задаваемые вопросы</b>\n\nВыберите тему:",
        reply_markup=faq_categories_keyboard(categories),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("faq_") & ~F.data.startswith("faqq_"))
async def show_faq_category(callback: CallbackQuery):
    category = callback.data[4:]  # Remove "faq_"

    if category == "custom":
        await callback.message.edit_text(
            "💬 Напишите ваш вопрос, и мы ответим в ближайшее время!\n"
            "Просто отправьте сообщение в этот чат."
        )
        await callback.answer()
        return

    async with async_session() as session:
        result = await session.execute(
            select(FAQ)
            .where(FAQ.category == category, FAQ.is_active == True)
            .order_by(FAQ.sort_order)
        )
        faqs = result.scalars().all()

    questions = [{"id": f.id, "question": f.question} for f in faqs]
    await callback.message.edit_text(
        f"❓ <b>{category}</b>\n\nВыберите вопрос:",
        reply_markup=faq_questions_keyboard(questions, category),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("faqq_"))
async def show_faq_answer(callback: CallbackQuery):
    faq_id = int(callback.data.split("_")[1])

    async with async_session() as session:
        faq = await session.get(FAQ, faq_id)

    if not faq:
        await callback.answer("Вопрос не найден")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад к вопросам", callback_data=f"faq_{faq.category}")],
        [InlineKeyboardButton(text="🏠 Все категории", callback_data="back_faq")],
    ])

    await callback.message.edit_text(
        f"❓ <b>{faq.question}</b>\n\n{faq.answer}",
        reply_markup=keyboard,
    )
    await callback.answer()
