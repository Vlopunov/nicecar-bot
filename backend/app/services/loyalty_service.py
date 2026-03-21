from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import BonusTransaction, BonusType, User


async def earn_cashback(session: AsyncSession, user_id: int, booking_id: int, amount: Decimal) -> BonusTransaction:
    """Award cashback after a completed booking."""
    cashback = amount * Decimal(settings.CASHBACK_PERCENT) / Decimal(100)
    if cashback <= 0:
        return None

    tx = BonusTransaction(
        user_id=user_id,
        amount=cashback,
        type=BonusType.CASHBACK,
        booking_id=booking_id,
        description=f"Кэшбэк {settings.CASHBACK_PERCENT}% от визита",
    )
    session.add(tx)

    user = await session.get(User, user_id)
    user.bonus_balance += cashback
    await session.commit()
    return tx


async def process_referral(session: AsyncSession, referrer_id: int, referred_id: int) -> None:
    """Process referral bonuses when referred user makes first visit."""
    # Bonus for referrer
    tx_referrer = BonusTransaction(
        user_id=referrer_id,
        amount=Decimal(settings.REFERRAL_BONUS),
        type=BonusType.REFERRAL_BONUS,
        description=f"Бонус за приглашённого друга",
    )
    session.add(tx_referrer)

    referrer = await session.get(User, referrer_id)
    referrer.bonus_balance += Decimal(settings.REFERRAL_BONUS)

    # Welcome bonus for referred
    tx_referred = BonusTransaction(
        user_id=referred_id,
        amount=Decimal(settings.REFERRAL_WELCOME_BONUS),
        type=BonusType.REFERRAL_WELCOME,
        description="Приветственный бонус по приглашению",
    )
    session.add(tx_referred)

    referred = await session.get(User, referred_id)
    referred.bonus_balance += Decimal(settings.REFERRAL_WELCOME_BONUS)

    await session.commit()


async def spend_bonus(session: AsyncSession, user_id: int, amount: Decimal, booking_id: int) -> BonusTransaction:
    """Spend bonus points on a booking."""
    user = await session.get(User, user_id)
    if user.bonus_balance < amount:
        raise ValueError("Недостаточно бонусов")

    tx = BonusTransaction(
        user_id=user_id,
        amount=-amount,
        type=BonusType.SPENT,
        booking_id=booking_id,
        description="Списание бонусов",
    )
    session.add(tx)
    user.bonus_balance -= amount
    await session.commit()
    return tx


async def get_bonus_transactions(session: AsyncSession, user_id: int) -> list[BonusTransaction]:
    result = await session.execute(
        select(BonusTransaction)
        .where(BonusTransaction.user_id == user_id)
        .order_by(BonusTransaction.created_at.desc())
    )
    return result.scalars().all()
