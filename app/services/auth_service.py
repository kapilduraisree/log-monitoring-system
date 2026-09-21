"""
Auth service — register, login, JWT, TOTP (Feature 10).
Uses native bcrypt to avoid passlib/bcrypt 4.x incompatibility (Bug Fix #8).
"""

import bcrypt
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


# ── User CRUD ─────────────────────────────────────────────────────────────────

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, username: str, email: str, password: str, role: str = "user") -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
        totp_enabled=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# ── Feature 10: TOTP 2FA ──────────────────────────────────────────────────────

def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_provisioning_uri(user: User) -> str:
    totp = pyotp.TOTP(user.totp_secret)
    return totp.provisioning_uri(name=user.email, issuer_name="LogMonitor")


def get_totp_qr_base64(user: User) -> str:
    """Return a base64-encoded PNG QR code for the TOTP setup."""
    uri = get_totp_provisioning_uri(user)
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def verify_totp(user: User, code: str) -> bool:
    if not user.totp_secret:
        return False
    totp = pyotp.TOTP(user.totp_secret)
    return totp.verify(code, valid_window=1)


def enable_totp(db: Session, user: User) -> str:
    secret = generate_totp_secret()
    user.totp_secret = secret
    user.totp_enabled = True
    db.commit()
    db.refresh(user)
    return secret


def disable_totp(db: Session, user: User) -> None:
    user.totp_secret = None
    user.totp_enabled = False
    db.commit()
