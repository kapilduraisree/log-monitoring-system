from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str
    totp_code: Optional[str] = None   # Feature 10


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    totp_enabled: bool

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    requires_totp: bool = False   # Feature 10 — tells frontend to prompt for OTP


class TOTPSetupOut(BaseModel):
    secret: str
    qr_code: str   # base64 PNG


class TOTPVerify(BaseModel):
    code: str
