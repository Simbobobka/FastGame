from functools import lru_cache
from typing import Type, TypeVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class RedisConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str
    port: int
    db: int


class ScrapersConfig(ConfigBase):

    django_api: str
    tabs_quantity: int = 5


class PlaywrightConfig(ConfigBase):

    playwright_ws_endpoint: str


ConfigType = TypeVar("ConfigType", bound=ConfigBase)


@lru_cache()
def get_config(config_class: Type[ConfigType]) -> ConfigType:
    """
    Universal fabric to create only one config
    """
    return config_class()
