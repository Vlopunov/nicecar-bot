from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session
from app.models import ServiceCategory, Service, ServicePrice
from app.bot.keyboards.inline import service_categories_keyboard, services_in_category_keyboard, service_detail_keyboard
from app.utils.helpers import format_price

router = Router()


@router.message(F.text == "📋 Услуги и цены")
async def show_categories(message: Message):
    async with async_session() as session:
        result = await session.execute(
            select(ServiceCategory)
            .where(ServiceCategory.is_active == True)
            .order_by(ServiceCategory.sort_order)
        )
        categories = result.scalars().all()

    cats = [{"id": c.id, "name": c.name, "icon": c.icon} for c in categories]
    await message.answer(
        "📋 <b>Выберите категорию услуг:</b>",
        reply_markup=service_categories_keyboard(cats),
    )


@router.callback_query(F.data == "back_categories")
async def back_to_categories(callback: CallbackQuery):
    async with async_session() as session:
        result = await session.execute(
            select(ServiceCategory)
            .where(ServiceCategory.is_active == True)
            .order_by(ServiceCategory.sort_order)
        )
        categories = result.scalars().all()

    cats = [{"id": c.id, "name": c.name, "icon": c.icon} for c in categories]
    await callback.message.edit_text(
        "📋 <b>Выберите категорию услуг:</b>",
        reply_markup=service_categories_keyboard(cats),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cat_"))
async def show_services(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])

    async with async_session() as session:
        result = await session.execute(
            select(Service)
            .where(Service.category_id == category_id, Service.is_active == True)
            .options(selectinload(Service.prices))
            .order_by(Service.sort_order)
        )
        services = result.scalars().all()

        cat_result = await session.execute(select(ServiceCategory).where(ServiceCategory.id == category_id))
        category = cat_result.scalar_one_or_none()

    if not services:
        await callback.answer("В этой категории пока нет услуг")
        return

    svcs = [{"id": s.id, "name": s.name} for s in services]
    cat_name = category.name if category else "Услуги"
    await callback.message.edit_text(
        f"📋 <b>{cat_name}</b>\n\nВыберите услугу:",
        reply_markup=services_in_category_keyboard(svcs, category_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("svc_"))
async def show_service_detail(callback: CallbackQuery):
    service_id = int(callback.data.split("_")[1])

    async with async_session() as session:
        result = await session.execute(
            select(Service)
            .where(Service.id == service_id)
            .options(selectinload(Service.prices))
        )
        service = result.scalar_one_or_none()

    if not service:
        await callback.answer("Услуга не найдена")
        return

    text = f"🔧 <b>{service.name}</b>\n\n"

    if service.description:
        text += f"{service.description}\n\n"

    if service.prices:
        if service.is_package:
            text += "<b>Пакеты:</b>\n"
            for p in service.prices:
                name = p.package_name or "Стандарт"
                text += f"\n📦 <b>{name}</b> — от {format_price(p.price_from)}\n"
                if p.description:
                    text += f"<i>{p.description}</i>\n"
        elif service.has_car_classes:
            text += "<b>Цены по классу авто:</b>\n"
            for p in service.prices:
                cls = p.car_class or "Общая"
                text += f"  • {cls} класс: от {format_price(p.price_from)}\n"
        else:
            p = service.prices[0]
            text += f"💰 От {format_price(p.price_from)}\n"

    duration_str = ""
    d_min = float(service.duration_min_hours)
    d_max = float(service.duration_max_hours)
    if d_min == d_max:
        duration_str = f"{d_min:.1f} ч"
    else:
        duration_str = f"{d_min:.1f}—{d_max:.1f} ч"
    text += f"\n⏱ Время выполнения: {duration_str}"

    await callback.message.edit_text(
        text,
        reply_markup=service_detail_keyboard(service_id),
    )
    await callback.answer()
