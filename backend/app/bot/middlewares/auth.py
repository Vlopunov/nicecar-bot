from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from sqlalchemy import select

from app.database import async_session
from app.models import User
from app.config import settings


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user = event.from_user
        if not user:
            return await handler(event, data)

        async with async_session() as session:
            result = await session.execute(select(User).where(User.telegram_id == user.id))
            db_user = result.scalar_one_or_none()

            if not db_user:
                db_user = User(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name or "",
                    last_name=user.last_name,
                    is_admin=user.id in settings.admin_ids_list,
                )
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)
            else:
                # Update username/name if changed
                changed = False
                if user.username and user.username != db_user.username:
                    db_user.username = user.username
                    changed = True
                if user.first_name and user.first_name != db_user.first_name:
                    db_user.first_name = user.first_name
                    changed = True
                if changed:
                    await session.commit()

        data["db_user"] = db_user
        return await handler(event, data)
