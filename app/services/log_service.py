"""Log entry service — CRUD + stats + timeline (Feature 9)."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, desc, asc
from sqlalchemy.orm import Session

from app.models.log_entry import LogEntry


def get_logs(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    search: Optional[str] = None,
    sort_desc: bool = True,
) -> dict:
    q = db.query(LogEntry)
    if severity:
        q = q.filter(LogEntry.severity == severity.upper())
    if event_type:
        q = q.filter(LogEntry.event_type == event_type)
    if search:
        q = q.filter(LogEntry.message.ilike(f"%{search}%"))
    total = q.count()
    order = desc(LogEntry.timestamp) if sort_desc else asc(LogEntry.timestamp)
    items = q.order_by(order).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}


def get_log_by_id(db: Session, log_id: int) -> Optional[LogEntry]:
    return db.query(LogEntry).filter(LogEntry.id == log_id).first()


def delete_log(db: Session, log_id: int) -> bool:
    entry = get_log_by_id(db, log_id)
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True


def get_stats(db: Session) -> dict:
    """7 severity counts + today count."""
    counts = (
        db.query(LogEntry.severity, func.count(LogEntry.id))
        .group_by(LogEntry.severity)
        .all()
    )
    result = {s: 0 for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")}
    for sev, cnt in counts:
        if sev in result:
            result[sev] = cnt
    result["total"] = sum(result.values())

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    result["today"] = (
        db.query(func.count(LogEntry.id))
        .filter(LogEntry.timestamp >= today_start)
        .scalar()
        or 0
    )
    return result


def get_hourly_events(db: Session) -> list[dict]:
    """Events-per-hour for the last 24 h — Bug Fix #7: Z-suffix for UTC."""
    since = datetime.utcnow() - timedelta(hours=24)
    rows = (
        db.query(
            func.strftime("%Y-%m-%dT%H:00:00Z", LogEntry.timestamp).label("hour"),
            func.count(LogEntry.id).label("count"),
        )
        .filter(LogEntry.timestamp >= since)
        .group_by("hour")
        .order_by("hour")
        .all()
    )
    return [{"hour": r.hour, "count": r.count} for r in rows]


def get_top_ips(db: Session, limit: int = 10) -> list[dict]:
    rows = (
        db.query(LogEntry.source_ip, func.count(LogEntry.id).label("count"))
        .filter(LogEntry.source_ip != None)  # noqa: E711
        .group_by(LogEntry.source_ip)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )
    return [{"ip": r.source_ip, "count": r.count} for r in rows]


def get_attack_categories(db: Session) -> list[dict]:
    rows = (
        db.query(LogEntry.event_type, func.count(LogEntry.id).label("count"))
        .filter(LogEntry.event_type != None)  # noqa: E711
        .group_by(LogEntry.event_type)
        .order_by(desc("count"))
        .all()
    )
    return [{"type": r.event_type, "count": r.count} for r in rows]


# ── Feature 9: Threat Timeline ────────────────────────────────────────────────

def get_threat_timeline(db: Session, ip: Optional[str] = None, limit: int = 200) -> list[dict]:
    """
    Return a chronological list of security events for the timeline view.
    If *ip* is provided, filter to that IP only.
    """
    q = db.query(LogEntry).filter(
        LogEntry.severity.in_(["CRITICAL", "HIGH", "MEDIUM"])
    )
    if ip:
        q = q.filter(LogEntry.source_ip == ip)
    rows = q.order_by(asc(LogEntry.timestamp)).limit(limit).all()
    return [
        {
            "id":         r.id,
            "timestamp":  r.timestamp.isoformat() + "Z",
            "source_ip":  r.source_ip,
            "severity":   r.severity,
            "event_type": r.event_type,
            "message":    r.message[:200],
            "geo_country": r.geo_country,
            "geo_city":   r.geo_city,
        }
        for r in rows
    ]
