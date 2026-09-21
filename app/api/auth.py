"""Auth routes — register, login (with TOTP), me, logout. Feature 10: 2FA."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database.engine import get_db
from app.schemas.user import UserCreate, UserLogin, UserOut, TokenOut, TOTPSetupOut, TOTPVerify
from app.services import auth_service
from app.services.audit_service import record as audit
from app.api.deps import get_current_user, get_client_ip
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(body: UserCreate, request: Request, db: Session = Depends(get_db)):
    if auth_service.get_user_by_username(db, body.username):
        raise HTTPException(400, "Username already taken")
    user = auth_service.create_user(db, body.username, body.email, body.password)
    audit(db, "REGISTER", user.id, user.username, "/auth/register",
          ip_address=get_client_ip(request))
    return user


@router.post("/login", response_model=TokenOut)
def login(body: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, body.username, body.password)
    if not user:
        audit(db, "LOGIN_FAILED", username=body.username, resource="/auth/login",
              ip_address=get_client_ip(request))
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    # Feature 10: TOTP check
    if user.totp_enabled:
        if not body.totp_code:
            # Tell frontend to ask for OTP — issue a short-lived pre-auth token
            pre_token = auth_service.create_access_token(
                {"sub": str(user.id), "totp_pending": True},
            )
            return TokenOut(access_token=pre_token, requires_totp=True)
        if not auth_service.verify_totp(user, body.totp_code):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid TOTP code")

    token = auth_service.create_access_token({"sub": str(user.id)})
    audit(db, "LOGIN", user.id, user.username, "/auth/login",
          ip_address=get_client_ip(request))
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(request: Request, current_user: User = Depends(get_current_user),
           db: Session = Depends(get_db)):
    audit(db, "LOGOUT", current_user.id, current_user.username,
          ip_address=get_client_ip(request))
    return {"detail": "Logged out"}


# ── Feature 10: TOTP management ───────────────────────────────────────────────

@router.post("/totp/setup", response_model=TOTPSetupOut)
def totp_setup(current_user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    """Generate a new TOTP secret and return QR code (base64 PNG)."""
    secret = auth_service.enable_totp(db, current_user)
    qr     = auth_service.get_totp_qr_base64(current_user)
    return TOTPSetupOut(secret=secret, qr_code=qr)


@router.post("/totp/verify")
def totp_verify(body: TOTPVerify, current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    """Confirm TOTP code to finalize setup."""
    if not auth_service.verify_totp(current_user, body.code):
        raise HTTPException(400, "Invalid TOTP code")
    return {"detail": "TOTP verified and enabled"}


@router.post("/totp/disable")
def totp_disable(body: TOTPVerify, current_user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    """Disable TOTP — requires current valid code."""
    if not auth_service.verify_totp(current_user, body.code):
        raise HTTPException(400, "Invalid TOTP code")
    auth_service.disable_totp(db, current_user)
    return {"detail": "TOTP disabled"}
