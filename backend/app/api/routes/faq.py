from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import FAQ

router = APIRouter(prefix="/api/faq", tags=["faq"])


@router.get("")
async def get_faq(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(FAQ).where(FAQ.is_active == True).order_by(FAQ.category, FAQ.sort_order)
    )
    faqs = result.scalars().all()

    # Group by category
    categories = {}
    for faq in faqs:
        if faq.category not in categories:
            categories[faq.category] = []
        categories[faq.category].append({
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer,
        })

    return [{"category": cat, "items": items} for cat, items in categories.items()]
