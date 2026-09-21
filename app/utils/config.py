"""Application settings loaded from .env via pydantic-settings."""

from pydantic_settings import BaseSettings
from typing import List


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

    # ── CORS — accepts comma-separated origins ────────────────────────────────
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
    EMAIL_TO: str = ""
    EMAIL_USE_TLS: bool = True

    # ── Feature 5: Scheduled reports ──────────────────────────────────────────
    REPORT_SCHEDULE_ENABLED: bool = False
    REPORT_SCHEDULE_HOUR: int = 7
    REPORT_EMAIL_TO: str = ""

    def get_cors_origins(self) -> List[str]:
        """Return list of allowed CORS origins (supports comma-separated)."""
        origins = [o.strip() for o in self.FRONTEND_URL.split(",") if o.strip()]
        # Always allow localhost for development
        defaults = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ]
        return list(set(origins + defaults))

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
