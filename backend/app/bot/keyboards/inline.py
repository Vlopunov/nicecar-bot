from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from app.config import settings


def service_categories_keyboard(categories: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(
            text=f"{cat['icon']} {cat['name']}",
            callback_data=f"cat_{cat['id']}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def services_in_category_keyboard(services: list[dict], category_id: int) -> InlineKeyboardMarkup:
    buttons = []
    for s in services:
        buttons.append([InlineKeyboardButton(
            text=s["name"],
            callback_data=f"svc_{s['id']}",
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Назад к категориям", callback_data="back_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def service_detail_keyboard(service_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📅 Записаться на эту услугу",
            web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/booking?service={service_id}"),
        )],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_categories")],
    ])


def car_class_keyboard(service_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="I класс (Golf, Focus, Solaris)", callback_data=f"class_{service_id}_I")],
        [InlineKeyboardButton(text="II класс (RAV4, Tiguan, Mazda 6)", callback_data=f"class_{service_id}_II")],
        [InlineKeyboardButton(text="III класс (BMW 7, X-Trail, Q5)", callback_data=f"class_{service_id}_III")],
    ])


def faq_categories_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=cat, callback_data=f"faq_{cat}")])
    buttons.append([InlineKeyboardButton(text="💬 Задать свой вопрос", callback_data="faq_custom")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def faq_questions_keyboard(questions: list[dict], category: str) -> InlineKeyboardMarkup:
    buttons = []
    for q in questions:
        text = q["question"][:50] + "..." if len(q["question"]) > 50 else q["question"]
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"faqq_{q['id']}")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_faq")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def booking_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="booking_confirm"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="booking_cancel"),
        ],
    ])
