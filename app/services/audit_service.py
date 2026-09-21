"""Feature 4: User Activity Audit Log service."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def record(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    resource: Optional[str] = None,
    detail: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    entry = AuditLog(
        created_at=datetime.utcnow(),
        user_id=user_id,
        username=username,
        action=action,
        resource=resource,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_audit_logs(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    username: Optional[str] = None,
    action: Optional[str] = None,
) -> dict:
    q = db.query(AuditLog)
    if username:
        q = q.filter(AuditLog.username.ilike(f"%{username}%"))
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    total = q.count()
    items = q.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}
