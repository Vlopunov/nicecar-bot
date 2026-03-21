from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.api.deps import get_admin_user
from app.models import WorkPost, BlockedSlot, User

router = APIRouter(prefix="/api/admin/posts", tags=["admin-posts"])


class PostData(BaseModel):
    name: str
    specialization: str | None = None
    is_active: bool = True


class BlockedSlotData(BaseModel):
    post_id: int | None = None
    date: str
    time_start: str
    time_end: str
    reason: str = ""


@router.get("")
async def list_posts(_: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(WorkPost).order_by(WorkPost.id))
    posts = result.scalars().all()
    return [{"id": p.id, "name": p.name, "specialization": p.specialization, "is_active": p.is_active} for p in posts]


@router.post("")
async def create_post(data: PostData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    post = WorkPost(**data.model_dump())
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return {"id": post.id, "name": post.name}


@router.put("/{post_id}")
async def update_post(post_id: int, data: PostData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    post = await session.get(WorkPost, post_id)
    if not post:
        return {"error": "Not found"}
    for k, v in data.model_dump().items():
        setattr(post, k, v)
    await session.commit()
    return {"id": post.id}


# Blocked slots
@router.post("/blocked-slots")
async def create_blocked_slot(data: BlockedSlotData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    from datetime import date as date_type, time

    slot = BlockedSlot(
        post_id=data.post_id,
        date=date_type.fromisoformat(data.date),
        time_start=time.fromisoformat(data.time_start),
        time_end=time.fromisoformat(data.time_end),
        reason=data.reason,
    )
    session.add(slot)
    await session.commit()
    return {"id": slot.id}


@router.delete("/blocked-slots/{slot_id}")
async def delete_blocked_slot(slot_id: int, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    slot = await session.get(BlockedSlot, slot_id)
    if not slot:
        return {"error": "Not found"}
    await session.delete(slot)
    await session.commit()
    return {"ok": True}
