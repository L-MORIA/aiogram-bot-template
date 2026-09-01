from database.db import get_db

async def register_user(user_id: int, first_name: str, username: str | None) -> None:
    async for db in get_db():
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, first_name, username)
            VALUES (?, ?, ?)
        """, (user_id, first_name, username))
        await db.commit()

async def is_admin(user_id: int) -> bool:
    async for db in get_db():
        cur = await db.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return bool(row and row["is_admin"])

async def log_action(user_id: int, action: str) -> None:
    async for db in get_db():
        await db.execute(
            "INSERT INTO bot_logs (user_id, action) VALUES (?, ?)",
            (user_id, action)
        )
        await db.commit()

async def get_stats() -> dict:
    async for db in get_db():
        total = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        active_today = await (await db.execute(
            "SELECT COUNT(DISTINCT user_id) FROM bot_logs WHERE date(created_at) = date('now')"
        )).fetchone()
        actions = await (await db.execute(
            "SELECT action, COUNT(*) as cnt FROM bot_logs GROUP BY action ORDER BY cnt DESC"
        )).fetchall()
        return {
            "total_users": total[0] if total else 0,
            "active_today": active_today[0] if active_today else 0,
            "actions": {row["action"]: row["cnt"] for row in actions}
        }