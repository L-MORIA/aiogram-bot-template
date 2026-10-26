from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite

from config import config

DB_PATH = Path(config.db_path)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            first_name  TEXT NOT NULL,
            username    TEXT,
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


@asynccontextmanager
async def get_db():
    """Соединение как контекстный менеджер: закрывается строго после блока.

    aiosqlite-соединение — это non-daemon поток; не закрытое явно,
    оно навсегда блокирует завершение процесса (актуально для тестов и CLI).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # SQLite не включает проверку внешних ключей по умолчанию,
        # pragma действует только на текущее соединение.
        await db.execute("PRAGMA foreign_keys = ON")
        db.row_factory = aiosqlite.Row
        yield db
