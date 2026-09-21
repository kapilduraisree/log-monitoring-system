"""Feature 4: Audit Log routes — admin only."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.engine import get_db
from app.schemas.audit import AuditLogOut, AuditLogsPage
from app.services.audit_service import get_audit_logs
from app.api.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditLogsPage)
def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    username: Optional[str] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = get_audit_logs(db, page, page_size, username, action)
    return AuditLogsPage(**result)
