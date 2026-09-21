"""Create all tables and seed the default admin user."""

import bcrypt
from sqlalchemy.orm import Session

from app.database.engine import engine, Base, SessionLocal
from app.utils.config import settings

# Import all models so Base knows about them
from app.models import user, log_entry, alert, audit_log, suppression_rule, monitor_target  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        _seed_admin(db)
    finally:
        db.close()


def _seed_admin(db: Session) -> None:
    from app.models.user import User

    existing = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
    if existing:
        return

    hashed = bcrypt.hashpw(settings.ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
    admin = User(
        username=settings.ADMIN_USERNAME,
        email=f"{settings.ADMIN_USERNAME}@localhost",
        hashed_password=hashed,
        role="admin",
        is_active=True,
        totp_enabled=False,
    )
    db.add(admin)
    db.commit()
