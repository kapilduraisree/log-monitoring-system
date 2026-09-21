"""Log entry routes — list, stats, detail, delete, timeline (Feature 9)."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database.engine import get_db
from app.schemas.log_entry import LogEntryOut, LogsPage
from app.services import log_service
from app.services.audit_service import record as audit
from app.api.deps import get_current_user, require_admin, get_client_ip
from app.models.user import User

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=LogsPage)
def list_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    search: Optional[str] = None,
    sort_desc: bool = True,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = log_service.get_logs(db, page, page_size, severity, event_type, search, sort_desc)
    return LogsPage(**result)


@router.get("/stats")
def log_stats(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return log_service.get_stats(db)


@router.get("/hourly")
def hourly_events(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return log_service.get_hourly_events(db)


@router.get("/top-ips")
def top_ips(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return log_service.get_top_ips(db, limit)


@router.get("/attack-categories")
def attack_categories(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return log_service.get_attack_categories(db)


# ── Feature 9: Threat Timeline ────────────────────────────────────────────────
@router.get("/timeline")
def threat_timeline(
    ip: Optional[str] = None,
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return log_service.get_threat_timeline(db, ip, limit)


@router.get("/{log_id}", response_model=LogEntryOut)
def get_log(log_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    entry = log_service.get_log_by_id(db, log_id)
    if not entry:
        raise HTTPException(404, "Log entry not found")
    return entry


@router.delete("/{log_id}")
def delete_log(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    ok = log_service.delete_log(db, log_id)
    if not ok:
        raise HTTPException(404, "Log entry not found")
    audit(db, "DELETE_LOG", admin.id, admin.username, f"/logs/{log_id}",
          ip_address=get_client_ip(request))
    return {"detail": "Deleted"}
