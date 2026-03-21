import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message


class ThrottleMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self._cache: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        now = time.monotonic()
        last = self._cache.get(user_id, 0)

        if now - last < self.rate_limit:
            return  # Skip throttled message

        self._cache[user_id] = now

        # Clean old entries periodically
        if len(self._cache) > 10000:
            cutoff = now - 60
            self._cache = {k: v for k, v in self._cache.items() if v > cutoff}

        return await handler(event, data)
