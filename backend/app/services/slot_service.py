from datetime import date, time, timedelta, datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Booking, BookingStatus, WorkPost, BlockedSlot
from app.utils.helpers import get_work_hours, is_working_day


async def get_available_slots(
    session: AsyncSession,
    target_date: date,
    service_duration_hours: float,
) -> list[time]:
    """Get available time slots for a given date and service duration."""
    if not is_working_day(target_date):
        return []

    work_hours = get_work_hours(target_date)
    if not work_hours:
        return []

    work_start, work_end = work_hours

    # Get active posts
    posts_result = await session.execute(select(WorkPost).where(WorkPost.is_active == True))
    posts = posts_result.scalars().all()
    if not posts:
        return []

    post_ids = [p.id for p in posts]

    # Get existing bookings for the date
    bookings_result = await session.execute(
        select(Booking).where(
            and_(
                Booking.date == target_date,
                Booking.status.not_in([BookingStatus.CANCELLED, BookingStatus.NO_SHOW]),
            )
        )
    )
    bookings = bookings_result.scalars().all()

    # Get blocked slots for the date
    blocked_result = await session.execute(
        select(BlockedSlot).where(BlockedSlot.date == target_date)
    )
    blocked_slots = blocked_result.scalars().all()

    duration_minutes = int(service_duration_hours * 60)
    available = []

    # Generate slots in 30-minute intervals
    current = datetime.combine(target_date, work_start)
    end_boundary = datetime.combine(target_date, work_end)

    while current + timedelta(minutes=duration_minutes) <= end_boundary:
        slot_start = current.time()
        slot_end = (current + timedelta(minutes=duration_minutes)).time()

        # Count how many posts are occupied during this slot
        occupied_posts = set()

        for booking in bookings:
            if _times_overlap(slot_start, slot_end, booking.time_start, booking.time_end):
                if booking.post_id:
                    occupied_posts.add(booking.post_id)
                else:
                    occupied_posts.add(f"unassigned_{booking.id}")

        for blocked in blocked_slots:
            if _times_overlap(slot_start, slot_end, blocked.time_start, blocked.time_end):
                if blocked.post_id:
                    occupied_posts.add(blocked.post_id)
                else:
                    # All posts blocked
                    occupied_posts.update(post_ids)

        free_posts = len(post_ids) - len(occupied_posts.intersection(set(post_ids)))
        # Count unassigned bookings
        unassigned_count = sum(1 for k in occupied_posts if isinstance(k, str) and k.startswith("unassigned_"))
        free_posts = max(0, free_posts - unassigned_count)

        if free_posts > 0:
            available.append(slot_start)

        current += timedelta(minutes=30)

    return available


def _times_overlap(start1: time, end1: time, start2: time, end2: time) -> bool:
    return start1 < end2 and start2 < end1
