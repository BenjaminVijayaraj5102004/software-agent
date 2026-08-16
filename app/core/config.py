import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY: SecretStr

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cli_access_token_expire_hours: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

