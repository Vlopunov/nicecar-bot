from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Service
from app.services.slot_service import get_available_slots

router = APIRouter(prefix="/api/slots", tags=["slots"])


@router.get("")
async def get_slots(
    date_str: str = Query(..., alias="date"),
    service_id: int = Query(...),
    session: AsyncSession = Depends(get_session),
):
    """Get available time slots for a date and service."""
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        return {"error": "Invalid date format, use YYYY-MM-DD"}

    service = await session.get(Service, service_id)
    if not service:
        return {"error": "Service not found"}

    slots = await get_available_slots(session, target_date, float(service.duration_max_hours))
    return {
        "date": date_str,
        "service_id": service_id,
        "slots": [s.strftime("%H:%M") for s in slots],
    }
