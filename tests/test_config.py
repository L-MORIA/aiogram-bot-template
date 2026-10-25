import pytest
from pydantic import ValidationError

from config import Config


def test_admin_ids_comma_separated():
    assert Config(bot_token="x", admin_ids="111,222,333").admin_ids == [111, 222, 333]


def test_admin_ids_comma_with_spaces():
    assert Config(bot_token="x", admin_ids=" 1 , 2 , 3 ").admin_ids == [1, 2, 3]


def test_admin_ids_json_format():
    assert Config(bot_token="x", admin_ids="[7, 8]").admin_ids == [7, 8]


def test_admin_ids_default_empty(monkeypatch):
    monkeypatch.delenv("ADMIN_IDS", raising=False)
    assert Config(bot_token="x").admin_ids == []


def test_admin_ids_rejects_garbage():
    with pytest.raises(ValidationError):
        Config(bot_token="x", admin_ids="abc,def")


def test_bot_token_required(monkeypatch):
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    # _env_file=None — чтобы локальный .env разработчика не влиял на тест
    with pytest.raises(ValidationError):
        Config(_env_file=None)
