"""Alert service — CRUD + acknowledgement (Feature 3)."""

from datetime import datetime
from typing import Optional

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.models.alert import Alert


def get_alerts(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
) -> dict:
    q = db.query(Alert)
    if alert_type:
        q = q.filter(Alert.alert_type == alert_type)
    if severity:
        q = q.filter(Alert.severity == severity.upper())
    if acknowledged is not None:
        q = q.filter(Alert.acknowledged == acknowledged)
    total = q.count()
    items = q.order_by(desc(Alert.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}


def get_alert_by_id(db: Session, alert_id: int) -> Optional[Alert]:
    return db.query(Alert).filter(Alert.id == alert_id).first()


def get_summary(db: Session) -> dict:
    counts = (
        db.query(Alert.severity, func.count(Alert.id))
        .group_by(Alert.severity)
        .all()
    )
    result = {s: 0 for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")}
    for sev, cnt in counts:
        if sev in result:
            result[sev] = cnt
    result["total"] = sum(result.values())
    result["unacknowledged"] = (
        db.query(func.count(Alert.id)).filter(Alert.acknowledged == False).scalar() or 0  # noqa: E712
    )
    return result


def get_critical_alerts(db: Session, limit: int = 20) -> list[Alert]:
    return (
        db.query(Alert)
        .filter(Alert.severity == "CRITICAL")
        .order_by(desc(Alert.created_at))
        .limit(limit)
        .all()
    )


# ── Feature 3: Alert Acknowledgement ─────────────────────────────────────────

def acknowledge_alert(
    db: Session,
    alert_id: int,
    user_id: int,
    note: Optional[str] = None,
) -> Optional[Alert]:
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        return None
    alert.acknowledged    = True
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = user_id
    alert.ack_note        = note
    db.commit()
    db.refresh(alert)
    return alert


def unacknowledge_alert(db: Session, alert_id: int) -> Optional[Alert]:
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        return None
    alert.acknowledged    = False
    alert.acknowledged_at = None
    alert.acknowledged_by = None
    alert.ack_note        = None
    db.commit()
    db.refresh(alert)
    return alert
