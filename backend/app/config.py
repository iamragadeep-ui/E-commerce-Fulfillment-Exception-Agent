from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="E-commerce Fulfillment Exception Agent")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    cors_origins: str = Field(default="http://localhost:3000,http://127.0.0.1:3000")
    database_url: str = Field(default="sqlite:///./app.db")
    log_level: str = Field(default="INFO")
    openai_api_key: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
