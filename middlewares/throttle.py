import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message


class ThrottlingMiddleware(BaseMiddleware):
    """Anti-flood: не пускает больше одного сообщения за rate_limit секунд.

    Админы (data["is_admin"], выставляется AdminMiddleware) обходят ограничение.
    Регистрировать после AdminMiddleware, чтобы флаг уже был в data.
    """

    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self._last_call: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user = event.from_user
        if user is not None and not data.get("is_admin"):
            now = time.monotonic()
            if now - self._last_call.get(user.id, 0.0) < self.rate_limit:
                return  # флуд — хендлер не вызывается
            self._last_call[user.id] = now
        return await handler(event, data)
