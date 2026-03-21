from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.database import get_session
from app.api.deps import get_admin_user
from app.models import Promotion, DiscountType, User

router = APIRouter(prefix="/api/admin/promotions", tags=["admin-promotions"])


class PromotionData(BaseModel):
    title: str
    description: str | None = None
    image_url: str | None = None
    discount_type: str = "percent"
    discount_value: float | None = None
    date_start: str
    date_end: str
    is_active: bool = True


@router.get("")
async def list_promotions(_: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Promotion).order_by(Promotion.date_end.desc()))
    promos = result.scalars().all()
    return [
        {
            "id": p.id, "title": p.title, "description": p.description,
            "discount_type": p.discount_type.value, "discount_value": float(p.discount_value) if p.discount_value else None,
            "date_start": p.date_start.isoformat(), "date_end": p.date_end.isoformat(),
            "is_active": p.is_active, "image_url": p.image_url,
        }
        for p in promos
    ]


@router.post("")
async def create_promotion(data: PromotionData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    promo = Promotion(
        title=data.title,
        description=data.description,
        image_url=data.image_url,
        discount_type=DiscountType(data.discount_type),
        discount_value=Decimal(str(data.discount_value)) if data.discount_value else None,
        date_start=date.fromisoformat(data.date_start),
        date_end=date.fromisoformat(data.date_end),
        is_active=data.is_active,
    )
    session.add(promo)
    await session.commit()
    await session.refresh(promo)
    return {"id": promo.id, "title": promo.title}


@router.put("/{promo_id}")
async def update_promotion(promo_id: int, data: PromotionData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    promo = await session.get(Promotion, promo_id)
    if not promo:
        return {"error": "Not found"}
    promo.title = data.title
    promo.description = data.description
    promo.image_url = data.image_url
    promo.discount_type = DiscountType(data.discount_type)
    promo.discount_value = Decimal(str(data.discount_value)) if data.discount_value else None
    promo.date_start = date.fromisoformat(data.date_start)
    promo.date_end = date.fromisoformat(data.date_end)
    promo.is_active = data.is_active
    await session.commit()
    return {"id": promo.id}


@router.delete("/{promo_id}")
async def delete_promotion(promo_id: int, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    promo = await session.get(Promotion, promo_id)
    if not promo:
        return {"error": "Not found"}
    await session.delete(promo)
    await session.commit()
    return {"ok": True}


# Public endpoint for active promotions
promotions_public_router = APIRouter(prefix="/api/promotions", tags=["promotions"])


@promotions_public_router.get("/active")
async def get_active_promotions(session: AsyncSession = Depends(get_session)):
    today = date.today()
    result = await session.execute(
        select(Promotion).where(
            Promotion.is_active == True,
            Promotion.date_start <= today,
            Promotion.date_end >= today,
        )
    )
    promos = result.scalars().all()
    return [
        {
            "id": p.id, "title": p.title, "description": p.description,
            "discount_type": p.discount_type.value,
            "discount_value": float(p.discount_value) if p.discount_value else None,
            "image_url": p.image_url,
            "date_end": p.date_end.isoformat(),
        }
        for p in promos
    ]
