from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.api.deps import get_admin_user
from app.models import FAQ, User

router = APIRouter(prefix="/api/admin/faq", tags=["admin-faq"])


class FAQData(BaseModel):
    category: str
    question: str
    answer: str
    sort_order: int = 0
    is_active: bool = True


@router.get("")
async def list_faq(_: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(FAQ).order_by(FAQ.category, FAQ.sort_order))
    faqs = result.scalars().all()
    return [
        {"id": f.id, "category": f.category, "question": f.question, "answer": f.answer,
         "sort_order": f.sort_order, "is_active": f.is_active}
        for f in faqs
    ]


@router.post("")
async def create_faq(data: FAQData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    faq = FAQ(**data.model_dump())
    session.add(faq)
    await session.commit()
    await session.refresh(faq)
    return {"id": faq.id}


@router.put("/{faq_id}")
async def update_faq(faq_id: int, data: FAQData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    faq = await session.get(FAQ, faq_id)
    if not faq:
        return {"error": "Not found"}
    for k, v in data.model_dump().items():
        setattr(faq, k, v)
    await session.commit()
    return {"id": faq.id}


@router.delete("/{faq_id}")
async def delete_faq(faq_id: int, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    faq = await session.get(FAQ, faq_id)
    if not faq:
        return {"error": "Not found"}
    await session.delete(faq)
    await session.commit()
    return {"ok": True}
