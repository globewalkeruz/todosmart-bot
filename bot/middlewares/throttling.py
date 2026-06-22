import time
from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate: float = 0.5) -> None:
        self._rate = rate
        self._last: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user = data.get("event_from_user")
            if user:
                now = time.monotonic()
                last = self._last.get(user.id, 0.0)
                if now - last < self._rate:
                    return  # silently drop
                self._last[user.id] = now
        return await handler(event, data)
