from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from bot.database.queries.groups import upsert_group, add_member


class GroupMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        chat = data.get("event_chat")
        user = data.get("event_from_user")
        db   = data.get("db")

        if db and chat and chat.type in ("group", "supergroup", "channel"):
            await upsert_group(db, chat.id, chat.title or "Unknown", chat.type)
            if user and not user.is_bot:
                await add_member(db, chat.id, user.id)

        return await handler(event, data)
