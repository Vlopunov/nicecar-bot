from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.api.deps import get_admin_user
from app.models import Booking, BookingStatus, User, WorkPost
from app.utils.helpers import now_minsk

router = APIRouter(prefix="/api/admin", tags=["admin-analytics"])


@router.get("/dashboard")
async def get_dashboard(_admin: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    today = now_minsk().date()
    tomorrow = today + timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_start = today.replace(day=1)

    # Today's bookings
    today_result = await session.execute(
        select(func.count()).select_from(Booking).where(Booking.date == today)
    )
    today_count = today_result.scalar() or 0

    # Tomorrow's bookings
    tomorrow_result = await session.execute(
        select(func.count()).select_from(Booking).where(Booking.date == tomorrow)
    )
    tomorrow_count = tomorrow_result.scalar() or 0

    # Revenue today
    rev_today = await session.execute(
        select(func.coalesce(func.sum(Booking.price_final), 0)).where(
            and_(Booking.date == today, Booking.status == BookingStatus.COMPLETED)
        )
    )
    revenue_today = float(rev_today.scalar() or 0)

    # Revenue this week
    rev_week = await session.execute(
        select(func.coalesce(func.sum(Booking.price_final), 0)).where(
            and_(Booking.date >= week_ago, Booking.status == BookingStatus.COMPLETED)
        )
    )
    revenue_week = float(rev_week.scalar() or 0)

    # Revenue this month
    rev_month = await session.execute(
        select(func.coalesce(func.sum(Booking.price_final), 0)).where(
            and_(Booking.date >= month_start, Booking.status == BookingStatus.COMPLETED)
        )
    )
    revenue_month = float(rev_month.scalar() or 0)

    # New clients this week
    new_clients = await session.execute(
        select(func.count()).select_from(User).where(
            and_(User.created_at >= week_ago.isoformat(), User.telegram_id > 0)
        )
    )
    new_clients_count = new_clients.scalar() or 0

    # Posts load (% filled today)
    posts_result = await session.execute(select(func.count()).select_from(WorkPost).where(WorkPost.is_active == True))
    total_posts = posts_result.scalar() or 1
    posts_load = min(100, int((today_count / (total_posts * 10)) * 100))  # rough estimate: 10 slots per post

    # Today's bookings by status
    status_result = await session.execute(
        select(Booking.status, func.count()).where(Booking.date == today).group_by(Booking.status)
    )
    status_counts = {row[0].value: row[1] for row in status_result.all()}

    return {
        "today_bookings": today_count,
        "tomorrow_bookings": tomorrow_count,
        "revenue_today": revenue_today,
        "revenue_week": revenue_week,
        "revenue_month": revenue_month,
        "new_clients_week": new_clients_count,
        "posts_load_percent": posts_load,
        "today_by_status": status_counts,
    }


@router.get("/schedule")
async def get_schedule(
    date_str: str = Query(None, alias="date"),
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    """Get schedule for a specific date (or today). Returns bookings organized by posts."""
    target = date.fromisoformat(date_str) if date_str else now_minsk().date()

    posts_result = await session.execute(select(WorkPost).where(WorkPost.is_active == True).order_by(WorkPost.id))
    posts = posts_result.scalars().all()

    bookings_result = await session.execute(
        select(Booking).where(
            and_(Booking.date == target, Booking.status.not_in([BookingStatus.CANCELLED]))
        ).order_by(Booking.time_start)
    )
    bookings = bookings_result.scalars().all()

    schedule = []
    for post in posts:
        post_bookings = [b for b in bookings if b.post_id == post.id]
        schedule.append({
            "post": {"id": post.id, "name": post.name},
            "bookings": [
                {
                    "id": b.id, "time_start": b.time_start.strftime("%H:%M"),
                    "time_end": b.time_end.strftime("%H:%M"),
                    "status": b.status.value,
                    "car": f"{b.car_brand} {b.car_model}",
                    "service_id": b.service_id,
                }
                for b in post_bookings
            ],
        })

    # Unassigned bookings
    unassigned = [b for b in bookings if b.post_id is None]
    if unassigned:
        schedule.append({
            "post": {"id": None, "name": "Не назначен"},
            "bookings": [
                {
                    "id": b.id, "time_start": b.time_start.strftime("%H:%M"),
                    "time_end": b.time_end.strftime("%H:%M"),
                    "status": b.status.value,
                    "car": f"{b.car_brand} {b.car_model}",
                    "service_id": b.service_id,
                }
                for b in unassigned
            ],
        })

    return {"date": target.isoformat(), "schedule": schedule}


@router.get("/analytics")
async def get_analytics(
    period: str = Query("month"),
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    today = now_minsk().date()
    if period == "week":
        start = today - timedelta(days=7)
    elif period == "month":
        start = today - timedelta(days=30)
    elif period == "year":
        start = today - timedelta(days=365)
    else:
        start = today - timedelta(days=30)

    # Total bookings in period
    total_bookings = await session.execute(
        select(func.count()).select_from(Booking).where(Booking.date >= start)
    )

    # Completed bookings
    completed = await session.execute(
        select(func.count()).select_from(Booking).where(
            and_(Booking.date >= start, Booking.status == BookingStatus.COMPLETED)
        )
    )

    # Total revenue
    revenue = await session.execute(
        select(func.coalesce(func.sum(Booking.price_final), 0)).where(
            and_(Booking.date >= start, Booking.status == BookingStatus.COMPLETED)
        )
    )

    # Average check
    avg_check = await session.execute(
        select(func.coalesce(func.avg(Booking.price_final), 0)).where(
            and_(Booking.date >= start, Booking.status == BookingStatus.COMPLETED)
        )
    )

    # Cancellations
    cancelled = await session.execute(
        select(func.count()).select_from(Booking).where(
            and_(Booking.date >= start, Booking.status == BookingStatus.CANCELLED)
        )
    )

    return {
        "period": period,
        "date_from": start.isoformat(),
        "date_to": today.isoformat(),
        "total_bookings": total_bookings.scalar() or 0,
        "completed_bookings": completed.scalar() or 0,
        "cancelled_bookings": cancelled.scalar() or 0,
        "total_revenue": float(revenue.scalar() or 0),
        "average_check": float(avg_check.scalar() or 0),
    }
