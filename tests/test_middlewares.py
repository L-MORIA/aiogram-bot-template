"""Тесты middlewares: AdminMiddleware и ThrottlingMiddleware."""
from types import SimpleNamespace

import pytest

import middlewares.admin
from database import repository
from database.db import get_db
from middlewares.admin import AdminMiddleware
from middlewares.throttle import ThrottlingMiddleware


class FakeMessage:
    def __init__(self, user_id: int | None):
        self.from_user = SimpleNamespace(id=user_id) if user_id is not None else None


async def run_middleware(mw, message, data=None):
    calls = []

    async def handler(event, d):
        calls.append(d)
        return d.get("is_admin")

    result = await mw(handler, message, data or {})
    return result, calls


class TestAdminMiddleware:
    @pytest.mark.usefixtures("db")
    async def test_from_user_none_is_not_admin_and_no_crash(self):
        result, calls = await run_middleware(AdminMiddleware(), FakeMessage(None))
        assert result is False
        assert calls  # хендлер всё равно вызван

    @pytest.mark.usefixtures("db")
    async def test_env_admin(self, monkeypatch):
        monkeypatch.setattr(middlewares.admin, "config", SimpleNamespace(admin_ids=[42]))
        result, _ = await run_middleware(AdminMiddleware(), FakeMessage(42))
        assert result is True

    @pytest.mark.usefixtures("db")
    async def test_db_admin(self, monkeypatch):
        monkeypatch.setattr(middlewares.admin, "config", SimpleNamespace(admin_ids=[]))
        await repository.register_user(42, "Admin", None)
        async for conn in get_db():
            await conn.execute("UPDATE users SET is_admin = 1 WHERE user_id = 42")
            await conn.commit()
        result, _ = await run_middleware(AdminMiddleware(), FakeMessage(42))
        assert result is True

    @pytest.mark.usefixtures("db")
    async def test_regular_user(self, monkeypatch):
        monkeypatch.setattr(middlewares.admin, "config", SimpleNamespace(admin_ids=[]))
        await repository.register_user(1, "Bob", None)
        result, _ = await run_middleware(AdminMiddleware(), FakeMessage(1))
        assert result is False


class TestThrottlingMiddleware:
    @staticmethod
    async def _ok(event, data):
        return "ok"

    async def test_drops_rapid_messages(self):
        mw = ThrottlingMiddleware(rate_limit=10)
        results = [await mw(self._ok, FakeMessage(1), {"is_admin": False}) for _ in range(2)]
        assert results == ["ok", None]  # второе сообщение в пределах лимита — отброшено

    async def test_admin_bypasses_throttle(self):
        mw = ThrottlingMiddleware(rate_limit=10)
        results = [await mw(self._ok, FakeMessage(1), {"is_admin": True}) for _ in range(2)]
        assert results == ["ok", "ok"]

    async def test_no_user_passes(self):
        mw = ThrottlingMiddleware(rate_limit=10)
        result = await mw(self._ok, FakeMessage(None), {})
        assert result == "ok"
