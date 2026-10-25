import json
from functools import lru_cache
from typing import Annotated, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(min_length=1)
    # NoDecode отключает JSON-парсинг значения из env — иначе формат
    # "1,2,3" падает с SettingsError ещё до валидатора.
    admin_ids: Annotated[list[int], NoDecode] = Field(default_factory=list)
    db_path: str = "bot.db"

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: Any) -> Any:
        # Допускаем оба формата: "1,2,3" и JSON-список "[1, 2, 3]".
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                return json.loads(value)
            return [int(item) for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_config() -> Config:
    return Config()


config = get_config()
