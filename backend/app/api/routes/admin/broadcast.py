from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.api.deps import get_admin_user
from app.models import Broadcast, BroadcastStatus, BroadcastSegment, User

router = APIRouter(prefix="/api/admin/broadcast", tags=["admin-broadcast"])


class BroadcastData(BaseModel):
    text: str
    image_url: str | None = None
    buttons: list[dict] | None = None
    segment: str = "all"
    segment_params: dict | None = None
    scheduled_at: str | None = None


@router.get("")
async def list_broadcasts(_: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Broadcast).order_by(Broadcast.created_at.desc()))
    broadcasts = result.scalars().all()
    return [
        {
            "id": b.id, "text": b.text[:100], "segment": b.segment.value,
            "status": b.status.value, "total_sent": b.total_sent,
            "total_errors": b.total_errors,
            "scheduled_at": b.scheduled_at.isoformat() if b.scheduled_at else None,
            "sent_at": b.sent_at.isoformat() if b.sent_at else None,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
        for b in broadcasts
    ]


@router.post("")
async def create_broadcast(
    data: BroadcastData,
    admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    from datetime import datetime

    broadcast = Broadcast(
        text=data.text,
        image_url=data.image_url,
        buttons=data.buttons,
        segment=BroadcastSegment(data.segment),
        segment_params=data.segment_params,
        scheduled_at=datetime.fromisoformat(data.scheduled_at) if data.scheduled_at else None,
        status=BroadcastStatus.SCHEDULED if data.scheduled_at else BroadcastStatus.DRAFT,
        created_by=admin.id,
    )
    session.add(broadcast)
    await session.commit()
    await session.refresh(broadcast)
    return {"id": broadcast.id, "status": broadcast.status.value}


@router.get("/{broadcast_id}")
async def get_broadcast(broadcast_id: int, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    broadcast = await session.get(Broadcast, broadcast_id)
    if not broadcast:
        return {"error": "Not found"}
    return {
        "id": broadcast.id, "text": broadcast.text, "image_url": broadcast.image_url,
        "buttons": broadcast.buttons, "segment": broadcast.segment.value,
        "segment_params": broadcast.segment_params, "status": broadcast.status.value,
        "total_sent": broadcast.total_sent, "total_errors": broadcast.total_errors,
        "scheduled_at": broadcast.scheduled_at.isoformat() if broadcast.scheduled_at else None,
        "sent_at": broadcast.sent_at.isoformat() if broadcast.sent_at else None,
    }
