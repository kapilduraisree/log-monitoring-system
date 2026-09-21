"""User ORM model — includes TOTP (2FA) fields."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database.engine import Base


class User(Base):
    __tablename__ = "users"

    id               = Column(Integer, primary_key=True, index=True)
    username         = Column(String(64), unique=True, index=True, nullable=False)
    email            = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password  = Column(String(256), nullable=False)
    role             = Column(String(16), default="user")          # "admin" | "user"
    is_active        = Column(Boolean, default=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    # ── Feature 10: Two-Factor Authentication ─────────────────────────────────
    totp_enabled     = Column(Boolean, default=False)
    totp_secret      = Column(String(64), nullable=True)           # base32 TOTP secret
