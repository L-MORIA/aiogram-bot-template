from database.db import get_db


async def register_user(user_id: int, first_name: str, username: str | None) -> None:
    async with get_db() as db:
        # Upsert: обновляет first_name/username при повторном /start
        # (username без UNIQUE — юзернейм может быть занят другим пользователем,
        # это не должно ломать регистрацию).
        await db.execute("""
            INSERT INTO users (user_id, first_name, username)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                first_name = excluded.first_name,
                username = excluded.username
        """, (user_id, first_name, username))
        await db.commit()


async def is_admin(user_id: int) -> bool:
    async with get_db() as db:
        cur = await db.execute(
            "SELECT is_admin FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cur.fetchone()
        return bool(row and row["is_admin"])


async def log_action(user_id: int, action: str) -> None:
    async with get_db() as db:
        # Пишем лог только для зарегистрированных пользователей,
        # иначе INSERT нарушит FOREIGN KEY (user_id -> users).
        await db.execute(
            """
            INSERT INTO bot_logs (user_id, action)
            SELECT ?, ?
            WHERE EXISTS (SELECT 1 FROM users WHERE user_id = ?)
            """,
            (user_id, action, user_id),
        )
        await db.commit()


async def cleanup_old_logs(days: int) -> int:
    """Удаляет записи bot_logs старше days дней, возвращает число удалённых.

    days <= 0 — ничего не удалять (хранить всё).
    """
    if days <= 0:
        return 0
    async with get_db() as db:
        # модификатор datetime передаём параметром, а не конкатенацией строки —
        # f-string в SQL ловится bandit как B608
        cur = await db.execute(
            "DELETE FROM bot_logs WHERE created_at < datetime('now', '-' || ? || ' days')",
            (days,),
        )
        await db.commit()
        return cur.rowcount or 0


async def get_stats() -> dict:
    async with get_db() as db:
        total = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        active_today = await (await db.execute(
            "SELECT COUNT(DISTINCT user_id) FROM bot_logs "
            "WHERE date(created_at) = date('now')"
        )).fetchone()
        actions = await (await db.execute(
            "SELECT action, COUNT(*) as cnt FROM bot_logs "
            "GROUP BY action ORDER BY cnt DESC"
        )).fetchall()
        return {
            "total_users": total[0] if total else 0,
            "active_today": active_today[0] if active_today else 0,
            "actions": {row["action"]: row["cnt"] for row in actions},
        }
