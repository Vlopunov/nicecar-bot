from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.api.deps import get_current_user
from app.models import User
from app.services.loyalty_service import get_bonus_transactions

router = APIRouter(prefix="/api/loyalty", tags=["loyalty"])


@router.get("")
async def get_loyalty(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    transactions = await get_bonus_transactions(session, user.id)
    return {
        "balance": float(user.bonus_balance),
        "cashback_percent": settings.CASHBACK_PERCENT,
        "max_usage_percent": settings.MAX_BONUS_USAGE_PERCENT,
        "transactions": [
            {
                "id": t.id,
                "amount": float(t.amount),
                "type": t.type.value,
                "description": t.description,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in transactions
        ],
    }


@router.get("/referral-link")
async def get_referral_link(user: User = Depends(get_current_user)):
    bot_username = settings.BOT_TOKEN.split(":")[0] if settings.BOT_TOKEN else "bot"
    return {
        "link": f"https://t.me/{bot_username}?start=ref_{user.id}",
        "referral_bonus": settings.REFERRAL_BONUS,
        "welcome_bonus": settings.REFERRAL_WELCOME_BONUS,
    }
