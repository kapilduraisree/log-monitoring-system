"""Alert routes — list, summary, critical, acknowledge (Feature 3)."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database.engine import get_db
from app.schemas.alert import AlertOut, AlertsPage, AckRequest
from app.services import alert_service
from app.services.audit_service import record as audit
from app.api.deps import get_current_user, get_client_ip
from app.models.user import User

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertsPage)
def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = alert_service.get_alerts(db, page, page_size, alert_type, severity, acknowledged)
    return AlertsPage(**result)


@router.get("/summary")
def alert_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return alert_service.get_summary(db)


@router.get("/critical")
def critical_alerts(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    alerts = alert_service.get_critical_alerts(db, limit)
    return [AlertOut.model_validate(a) for a in alerts]


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    alert = alert_service.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    return alert


# ── Feature 3: Acknowledge / Unacknowledge ────────────────────────────────────

@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge(
    alert_id: int,
    body: AckRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = alert_service.acknowledge_alert(db, alert_id, current_user.id, body.note)
    if not alert:
        raise HTTPException(404, "Alert not found")
    audit(db, "ACK_ALERT", current_user.id, current_user.username,
          f"/alerts/{alert_id}", detail=body.note,
          ip_address=get_client_ip(request))
    return alert


@router.post("/{alert_id}/unacknowledge", response_model=AlertOut)
def unacknowledge(
    alert_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = alert_service.unacknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    audit(db, "UNACK_ALERT", current_user.id, current_user.username,
          f"/alerts/{alert_id}", ip_address=get_client_ip(request))
    return alert
