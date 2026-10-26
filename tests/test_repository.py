"""Тесты database.repository: регистрация, upsert, логирование, статистика."""
import sqlite3

import pytest

from database.db import get_db
from database.repository import (
    cleanup_old_logs,
    get_stats,
    is_admin,
    log_action,
    register_user,
)


@pytest.mark.usefixtures("db")
async def test_register_users_with_same_username():
    # юзернейм занят другим пользователем — регистрация не должна теряться
    await register_user(1, "Alice", "alice")
    await register_user(2, "Bob", "alice")
    stats = await get_stats()
    assert stats["total_users"] == 2


@pytest.mark.usefixtures("db")
async def test_register_upsert_updates_fields():
    await register_user(1, "Alice", "alice")
    await register_user(1, "Alice II", None)
    stats = await get_stats()
    assert stats["total_users"] == 1  # тот же user_id — не задвоился
    async with get_db() as conn:
        cur = await conn.execute("SELECT first_name, username FROM users WHERE user_id = 1")
        row = await cur.fetchone()
    assert row["first_name"] == "Alice II"
    assert row["username"] is None


@pytest.mark.usefixtures("db")
async def test_is_admin():
    await register_user(1, "Alice", None)
    assert await is_admin(1) is False
    assert await is_admin(999) is False  # незарегистрированный
    async with get_db() as conn:
        await conn.execute("UPDATE users SET is_admin = 1 WHERE user_id = 1")
        await conn.commit()
    assert await is_admin(1) is True


@pytest.mark.usefixtures("db")
async def test_log_action_registered_and_not():
    await register_user(1, "Alice", None)
    await log_action(1, "/start")
    await log_action(999, "/stats")  # незарегистрированный — безопасно пропускается
    stats = await get_stats()
    assert stats["actions"] == {"/start": 1}


@pytest.mark.usefixtures("db")
async def test_foreign_keys_enforced():
    with pytest.raises(sqlite3.IntegrityError):
        async with get_db() as conn:
            await conn.execute("INSERT INTO bot_logs (user_id, action) VALUES (777, 'x')")
            await conn.commit()


@pytest.mark.usefixtures("db")
async def test_get_stats_counts():
    await register_user(1, "Alice", None)
    await register_user(2, "Bob", None)
    await log_action(1, "/start")
    await log_action(1, "/stats")
    stats = await get_stats()
    assert stats["total_users"] == 2
    assert stats["active_today"] == 1
    assert stats["actions"] == {"/start": 1, "/stats": 1}


@pytest.mark.usefixtures("db")
async def test_cleanup_old_logs():
    await register_user(1, "Alice", None)
    await log_action(1, "/start")
    async with get_db() as conn:
        # старая запись (40 дней назад) + свежая из log_action
        await conn.execute(
            "INSERT INTO bot_logs (user_id, action, created_at) "
            "VALUES (1, 'old', datetime('now', '-40 days'))"
        )
        await conn.commit()

    assert await cleanup_old_logs(30) == 1
    stats = await get_stats()
    assert stats["actions"] == {"/start": 1}


@pytest.mark.usefixtures("db")
async def test_cleanup_disabled_with_zero():
    await register_user(1, "Alice", None)
    await log_action(1, "/start")
    assert await cleanup_old_logs(0) == 0  # 0 = не удалять
    stats = await get_stats()
    assert stats["actions"] == {"/start": 1}
