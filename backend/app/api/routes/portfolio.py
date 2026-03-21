from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import PortfolioItem

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("")
async def get_portfolio(
    category_id: int | None = Query(None),
    session: AsyncSession = Depends(get_session),
):
    query = select(PortfolioItem).where(PortfolioItem.is_visible == True).order_by(PortfolioItem.created_at.desc())
    if category_id:
        query = query.where(PortfolioItem.category_id == category_id)

    result = await session.execute(query)
    items = result.scalars().all()

    return [
        {
            "id": item.id,
            "image_url": item.image_url,
            "image_before_url": item.image_before_url,
            "car_brand": item.car_brand,
            "car_model": item.car_model,
            "description": item.description,
            "category_id": item.category_id,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in items
    ]
