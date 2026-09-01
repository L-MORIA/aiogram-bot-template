from pydantic_settings import BaseSettings
from functools import lru_cache

class Config(BaseSettings):
    bot_token: str
    admin_ids: list[int] = []
    db_path: str = "bot.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache
def get_config() -> Config:
    return Config()

config = get_config()