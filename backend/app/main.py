import asyncio
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL), format="%(asctime)s %(name)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting NiceCar Bot & API...")

    # Create tables and seed data
    try:
        from app.database import engine, Base
        from app.models import *  # noqa: F401,F403
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")

        from app.seed import seed
        await seed()
    except Exception as e:
        logger.error(f"Database init error: {e}")

    bot_task = None
    if settings.BOT_TOKEN:
        from app.bot.bot import bot, dp
        from app.bot.handlers import start, services, booking, faq, photo, loyalty, admin
        from app.bot.middlewares.auth import AuthMiddleware
        from app.bot.middlewares.throttle import ThrottleMiddleware

        dp.message.middleware(ThrottleMiddleware())
        dp.message.middleware(AuthMiddleware())

        dp.include_router(start.router)
        dp.include_router(services.router)
        dp.include_router(booking.router)
        dp.include_router(faq.router)
        dp.include_router(photo.router)
        dp.include_router(loyalty.router)
        dp.include_router(admin.router)

        bot_task = asyncio.create_task(dp.start_polling(bot))
        logger.info("Telegram bot polling started")

    # Start scheduler for reminders
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        scheduler = AsyncIOScheduler(timezone="Europe/Minsk")
        scheduler.add_job(_send_reminders, "interval", minutes=15)
        scheduler.start()
        logger.info("Scheduler started")
    except Exception as e:
        logger.error(f"Scheduler failed to start: {e}")

    yield

    # Shutdown
    logger.info("Shutting down...")
    if bot_task and settings.BOT_TOKEN:
        from app.bot.bot import dp
        await dp.stop_polling()
        bot_task.cancel()


app = FastAPI(title="NiceCar Center API", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
import os
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "nicecar-bot"}


# Include routers
from app.api.routes.services import router as services_router
from app.api.routes.slots import router as slots_router
from app.api.routes.booking import router as booking_router
from app.api.routes.user import router as user_router
from app.api.routes.loyalty import router as loyalty_router
from app.api.routes.portfolio import router as portfolio_router
from app.api.routes.faq import router as faq_router
from app.api.routes.admin.bookings import router as admin_bookings_router
from app.api.routes.admin.services import router as admin_services_router
from app.api.routes.admin.users import router as admin_users_router
from app.api.routes.admin.portfolio import router as admin_portfolio_router
from app.api.routes.admin.promotions import router as admin_promotions_router, promotions_public_router
from app.api.routes.admin.broadcast import router as admin_broadcast_router
from app.api.routes.admin.posts import router as admin_posts_router
from app.api.routes.admin.analytics import router as admin_analytics_router
from app.api.routes.admin.faq import router as admin_faq_router

app.include_router(services_router)
app.include_router(slots_router)
app.include_router(booking_router)
app.include_router(user_router)
app.include_router(loyalty_router)
app.include_router(portfolio_router)
app.include_router(faq_router)
app.include_router(promotions_public_router)
app.include_router(admin_bookings_router)
app.include_router(admin_services_router)
app.include_router(admin_users_router)
app.include_router(admin_portfolio_router)
app.include_router(admin_promotions_router)
app.include_router(admin_broadcast_router)
app.include_router(admin_posts_router)
app.include_router(admin_analytics_router)
app.include_router(admin_faq_router)


async def _send_reminders():
    """Periodic task to send booking reminders."""
    from datetime import datetime, timedelta
    from sqlalchemy import select, and_
    from app.database import async_session
    from app.models import Booking, BookingStatus
    from app.utils.helpers import now_minsk

    now = now_minsk()

    async with async_session() as session:
        # 24h reminders
        target_24h = now + timedelta(hours=24)
        bookings_24h = await session.execute(
            select(Booking).where(
                and_(
                    Booking.date == target_24h.date(),
                    Booking.status == BookingStatus.CONFIRMED,
                    Booking.reminder_24h_sent == False,
                )
            )
        )
        for booking in bookings_24h.scalars().all():
            if settings.BOT_TOKEN:
                from app.bot.bot import bot
                from app.services.notification_service import send_reminder
                await send_reminder(bot, booking, 24)
                booking.reminder_24h_sent = True

        # 2h reminders
        target_2h = now + timedelta(hours=2)
        bookings_2h = await session.execute(
            select(Booking).where(
                and_(
                    Booking.date == target_2h.date(),
                    Booking.status == BookingStatus.CONFIRMED,
                    Booking.reminder_2h_sent == False,
                )
            )
        )
        for booking in bookings_2h.scalars().all():
            if settings.BOT_TOKEN:
                from app.bot.bot import bot
                from app.services.notification_service import send_reminder
                await send_reminder(bot, booking, 2)
                booking.reminder_2h_sent = True

        await session.commit()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.ENVIRONMENT == "development")
