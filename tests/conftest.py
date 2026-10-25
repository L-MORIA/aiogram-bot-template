"""Общие фикстуры и настройка окружения для тестов.

Переменные окружения задаются до импорта модулей проекта:
config.py и database/db.py читают их на этапе импорта.
"""
import os
import tempfile

os.environ.setdefault("BOT_TOKEN", "123456:TEST_TOKEN")
os.environ.setdefault("ADMIN_IDS", "111,222")
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(prefix="aiogram_template_test_"), "test.db")

import pytest

from database.db import DB_PATH, init_db


@pytest.fixture
async def db():
    """Свежая база для каждого теста."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    await init_db()
    yield
    if DB_PATH.exists():
        DB_PATH.unlink()
