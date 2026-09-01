import aiosqlite
from pathlib import Path

DB_PATH = Path("bot.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            first_name  TEXT NOT NULL,
            username    TEXT UNIQUE,
            joined_at   TEXT DEFAULT CURRENT_TIMESTAMP,
            is_admin    INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS bot_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            action      TEXT NOT NULL,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """)
        await db.commit()

async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db