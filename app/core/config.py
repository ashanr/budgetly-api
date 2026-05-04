from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "Budgetly AI Assistant API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./budgetly.db"
    DATABASE_ECHO: bool = False

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Redis
    REDIS_URL: Optional[str] = None

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Sentry
    SENTRY_DSN: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
