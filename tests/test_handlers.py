"""Тесты хендлеров: /start, /help, /stats (вызовы функций напрямую)."""
from types import SimpleNamespace

import pytest

from handlers.start_handler import cmd_help, cmd_start
from handlers.stats_handler import cmd_stats
from lexicon import LEXICON


class FakeMessage:
    def __init__(self, user_id: int | None = 1):
        if user_id is not None:
            self.from_user = SimpleNamespace(id=user_id, first_name="Test", username=None)
        else:
            self.from_user = None
        self.answers: list[str] = []
        self.reply_markups: list = []

    async def answer(self, text: str, reply_markup=None, **kwargs):
        self.answers.append(text)
        self.reply_markups.append(reply_markup)
        return None


@pytest.mark.usefixtures("db")
async def test_cmd_start_registers_and_replies_with_keyboard():
    msg = FakeMessage(user_id=1)
    await cmd_start(msg, is_admin=False)
    assert len(msg.answers) == 1
    assert msg.answers[0] == LEXICON["start"]
    assert msg.reply_markups[0] is not None  # главная клавиатура отправлена

    from database.repository import get_stats
    stats = await get_stats()
    assert stats["total_users"] == 1
    assert stats["actions"] == {"/start": 1}


@pytest.mark.usefixtures("db")
async def test_cmd_start_admin_gets_admin_keyboard():
    msg = FakeMessage(user_id=1)
    await cmd_start(msg, is_admin=True)
    # у админа в клавиатуре есть кнопка статистики
    keyboard = msg.reply_markups[0]
    texts = [btn.text for row in keyboard.keyboard for btn in row]
    assert "📊 Статистика" in texts


@pytest.mark.usefixtures("db")
async def test_cmd_start_without_user_is_safe():
    msg = FakeMessage(user_id=None)
    await cmd_start(msg, is_admin=False)
    assert msg.answers == []


@pytest.mark.usefixtures("db")
async def test_cmd_help():
    msg = FakeMessage(user_id=1)
    await cmd_help(msg)
    assert msg.answers == [LEXICON["help"]]


@pytest.mark.usefixtures("db")
async def test_cmd_stats_denies_non_admin():
    msg = FakeMessage(user_id=1)
    await cmd_stats(msg, is_admin=False)
    assert len(msg.answers) == 1
    assert "⛔" in msg.answers[0]


@pytest.mark.usefixtures("db")
async def test_cmd_stats_for_admin():
    from database.db import get_db
    from database.repository import get_stats, register_user

    await register_user(1, "Admin", None)
    async for conn in get_db():
        # действие с HTML-спецсимволами — должно попасть в вывод экранированным
        await conn.execute(
            "INSERT INTO bot_logs (user_id, action) VALUES (1, '<b>inject</b>')"
        )
        await conn.commit()

    msg = FakeMessage(user_id=1)
    await cmd_stats(msg, is_admin=True)
    text = msg.answers[0]
    assert "Статистика бота" in text
    assert "&lt;b&gt;inject&lt;/b&gt;" in text  # экранировано, не HTML-инъекция
    assert (await get_stats())["total_users"] == 1
