from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from config import config
from database.repository import is_admin


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        # from_user может быть None (например, сообщения от каналов) —
        # такие события админом не считаем.
        user = event.from_user
        if user is None:
            data["is_admin"] = False
            return await handler(event, data)
        data["is_admin"] = user.id in config.admin_ids or await is_admin(user.id)
        return await handler(event, data)
