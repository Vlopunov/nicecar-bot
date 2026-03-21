from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.api.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/api/user", tags=["user"])


class UserUpdate(BaseModel):
    phone: str | None = None
    first_name: str | None = None
    last_name: str | None = None


def _user_to_dict(u: User) -> dict:
    return {
        "id": u.id,
        "telegram_id": u.telegram_id,
        "username": u.username,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "phone": u.phone,
        "bonus_balance": float(u.bonus_balance),
        "total_spent": float(u.total_spent),
        "visit_count": u.visit_count,
        "tags": u.tags,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return _user_to_dict(user)


@router.put("/me")
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if data.phone is not None:
        user.phone = data.phone
    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name

    await session.commit()
    await session.refresh(user)
    return _user_to_dict(user)
