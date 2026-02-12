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


class SteamDBConfig(ConfigBase): ...


class GogConfig(ConfigBase):

    django_api: str


class PlaywrightConfig(ConfigBase):

    playwright_ws_endpoint: str


redis_config = RedisConfig()
gog_config = GogConfig()
playwright_config = PlaywrightConfig()
