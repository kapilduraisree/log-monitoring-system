"""Application settings loaded from .env via pydantic-settings."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./logs_security.db"

    # ── Auth ──────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-to-a-32-char-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # ── Admin seed ────────────────────────────────────────────────────────────
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "Admin@12345"

    # ── CORS ──────────────────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:5173"

    # ── Brute-force detection ─────────────────────────────────────────────────
    ALERT_THRESHOLD: int = 5
    BRUTE_FORCE_WINDOW: int = 300

    # ── File upload ───────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 50

    # ── Feature 1: Email alerts ───────────────────────────────────────────────
    EMAIL_HOST: str = ""
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    EMAIL_TO: str = ""          # comma-separated recipients
    EMAIL_USE_TLS: bool = True

    # ── Feature 5: Scheduled reports ──────────────────────────────────────────
    REPORT_SCHEDULE_ENABLED: bool = False
    REPORT_SCHEDULE_HOUR: int = 7           # UTC hour to send daily report
    REPORT_EMAIL_TO: str = ""               # override or reuse EMAIL_TO

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
