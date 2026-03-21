from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.api.deps import get_admin_user
from app.models import PortfolioItem, ServiceCategory, User
from app.services.instagram_parser import fetch_instagram_posts, guess_category_from_hashtags
from app.config import settings

router = APIRouter(prefix="/api/admin/portfolio", tags=["admin-portfolio"])


class PortfolioData(BaseModel):
    category_id: int | None = None
    service_id: int | None = None
    image_url: str
    image_before_url: str | None = None
    car_brand: str | None = None
    car_model: str | None = None
    description: str | None = None
    is_visible: bool = True


@router.get("")
async def list_portfolio(
    _: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(PortfolioItem).order_by(PortfolioItem.created_at.desc())
    )
    items = result.scalars().all()
    return [
        {
            "id": i.id, "image_url": i.image_url, "image_before_url": i.image_before_url,
            "car_brand": i.car_brand, "car_model": i.car_model, "description": i.description,
            "category_id": i.category_id, "is_visible": i.is_visible,
            "instagram_url": i.instagram_url,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i in items
    ]


@router.post("")
async def create_portfolio_item(
    data: PortfolioData,
    _: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    item = PortfolioItem(**data.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return {"id": item.id}


@router.put("/{item_id}")
async def update_portfolio_item(
    item_id: int,
    data: PortfolioData,
    _: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    item = await session.get(PortfolioItem, item_id)
    if not item:
        return {"error": "Not found"}
    for k, v in data.model_dump().items():
        setattr(item, k, v)
    await session.commit()
    return {"id": item.id}


@router.delete("/{item_id}")
async def delete_portfolio_item(
    item_id: int,
    _: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    item = await session.get(PortfolioItem, item_id)
    if not item:
        return {"error": "Not found"}
    await session.delete(item)
    await session.commit()
    return {"ok": True}


@router.post("/import-instagram")
async def import_from_instagram(
    _: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    """Fetch recent posts from Instagram and return for selection."""
    posts = await fetch_instagram_posts(settings.INSTAGRAM_USERNAME, count=12)

    # Resolve categories
    cats_result = await session.execute(select(ServiceCategory))
    categories = {c.name: c.id for c in cats_result.scalars().all()}

    result = []
    for post in posts:
        guessed = guess_category_from_hashtags(post.get("hashtags", []))
        result.append({
            "image_url": post["image_url"],
            "caption": post["caption"][:200],
            "permalink": post["permalink"],
            "guessed_category": guessed,
            "guessed_category_id": categories.get(guessed),
        })

    return result
