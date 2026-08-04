"""Application settings loaded from environment variables / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised application configuration."""

    APP_NAME: str = "AI Trading Analyst"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"

    DATABASE_URL: str = "sqlite+aiosqlite:///./trading_analyst.db"

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 1500

    NEWS_API_KEY: str = ""
    NEWS_ENABLED: bool = True

    MARKET_DATA_CACHE_TTL: int = 300
    SCANNER_BATCH_SIZE: int = 10
    SCANNER_MAX_WORKERS: int = 4
    DEFAULT_LOOKBACK_DAYS: int = 365

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 1

    DASHBOARD_PORT: int = 8501

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
