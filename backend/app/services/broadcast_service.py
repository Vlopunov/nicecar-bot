import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Broadcast, BroadcastStatus, BroadcastSegment, User, Booking

logger = logging.getLogger(__name__)


async def get_broadcast_audience(session: AsyncSession, broadcast: Broadcast) -> list[User]:
    """Get list of users matching broadcast segment."""
    query = select(User).where(User.telegram_id > 0)

    if broadcast.segment == BroadcastSegment.ALL:
        pass
    elif broadcast.segment == BroadcastSegment.VIP:
        query = query.where(User.tags.contains("vip"))
    elif broadcast.segment == BroadcastSegment.RECENT:
        days = (broadcast.segment_params or {}).get("days", 30)
        since = datetime.utcnow() - timedelta(days=days)
        query = query.where(
            User.id.in_(
                select(Booking.user_id).where(Booking.created_at >= since).distinct()
            )
        )
    elif broadcast.segment == BroadcastSegment.INACTIVE:
        days = (broadcast.segment_params or {}).get("days", 90)
        since = datetime.utcnow() - timedelta(days=days)
        query = query.where(
            User.id.not_in(
                select(Booking.user_id).where(Booking.created_at >= since).distinct()
            )
        )
    elif broadcast.segment == BroadcastSegment.BY_SERVICE:
        service_id = (broadcast.segment_params or {}).get("service_id")
        if service_id:
            query = query.where(
                User.id.in_(
                    select(Booking.user_id).where(Booking.service_id == service_id).distinct()
                )
            )

    result = await session.execute(query)
    return result.scalars().all()


async def send_broadcast(bot: Bot, session: AsyncSession, broadcast_id: int) -> None:
    """Execute broadcast sending with rate limiting."""
    broadcast = await session.get(Broadcast, broadcast_id)
    if not broadcast or broadcast.status == BroadcastStatus.SENT:
        return

    broadcast.status = BroadcastStatus.SENDING
    await session.commit()

    users = await get_broadcast_audience(session, broadcast)
    sent = 0
    errors = 0

    # Build keyboard if buttons defined
    keyboard = None
    if broadcast.buttons:
        buttons = []
        for btn in broadcast.buttons:
            buttons.append([InlineKeyboardButton(text=btn["text"], url=btn.get("url", ""))])
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    for user in users:
        try:
            if broadcast.image_url:
                await bot.send_photo(
                    user.telegram_id,
                    photo=broadcast.image_url,
                    caption=broadcast.text,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
            else:
                await bot.send_message(
                    user.telegram_id,
                    broadcast.text,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
            sent += 1
        except Exception as e:
            errors += 1
            logger.error(f"Broadcast send error for user {user.telegram_id}: {e}")

        # Rate limit: ~30 msg/sec
        if (sent + errors) % 30 == 0:
            await asyncio.sleep(1)

    broadcast.total_sent = sent
    broadcast.total_errors = errors
    broadcast.status = BroadcastStatus.SENT
    broadcast.sent_at = datetime.utcnow()
    await session.commit()
