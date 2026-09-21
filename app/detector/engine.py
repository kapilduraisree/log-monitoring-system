"""
Detection engine.

Evaluates parsed log events against all rules, enforces brute-force
heuristics (using log-event timestamps, not wall-clock time — Bug Fix #3),
and checks suppression rules (Feature 7) before creating alerts.
"""

from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.detector.rules import RULES, Rule
from app.detector.log_parser import parse_line
from app.models.log_entry import LogEntry
from app.models.alert import Alert
from app.models.suppression_rule import SuppressionRule
from app.utils.config import settings
from app.utils.geo import get_geo_sync
from app.utils.helpers import extract_ip
from app.utils.logger import get_logger

log = get_logger(__name__)

# Brute-force sliding window: {ip: [event_timestamp_float, ...]}
_bf_window: dict[str, list[float]] = defaultdict(list)


def _is_suppressed(db: Session, ip: Optional[str], message: str) -> bool:
    """Feature 7 — return True if this event matches any active suppression rule."""
    import re as _re
    rules: list[SuppressionRule] = (
        db.query(SuppressionRule).filter(SuppressionRule.is_active == True).all()  # noqa: E712
    )
    for r in rules:
        if r.rule_type == "ip" and ip and r.value == ip:
            return True
        if r.rule_type == "pattern":
            try:
                if _re.search(r.value, message, _re.IGNORECASE):
                    return True
            except Exception:
                pass
    return False


def _check_brute_force(ip: Optional[str], event_ts: float) -> bool:
    """Return True if this IP has exceeded ALERT_THRESHOLD in BRUTE_FORCE_WINDOW (log-time)."""
    if not ip:
        return False
    window = settings.BRUTE_FORCE_WINDOW
    threshold = settings.ALERT_THRESHOLD
    events = _bf_window[ip]
    events.append(event_ts)
    # Keep only events within the window relative to this event's timestamp
    _bf_window[ip] = [t for t in events if event_ts - t <= window]
    return len(_bf_window[ip]) >= threshold


def process_line(raw: str, source_file: str, db: Session) -> Optional[LogEntry]:
    """
    Parse *raw*, run detection, persist LogEntry + Alerts, return the entry.
    Returns None if the line is blank.
    """
    if not raw.strip():
        return None

    parsed = parse_line(raw, source_file)
    ip = parsed["source_ip"]
    message = parsed["message"]

    # ── Feature 2: Geo-lookup ─────────────────────────────────────────────────
    geo = get_geo_sync(ip) if ip else {}

    # ── Persist log entry ─────────────────────────────────────────────────────
    entry = LogEntry(
        timestamp   = parsed["timestamp"],
        source_file = parsed["source_file"],
        source_ip   = ip,
        severity    = parsed["severity"],
        message     = message,
        raw_line    = parsed["raw_line"],
        geo_country = geo.get("country"),
        geo_city    = geo.get("city"),
        geo_lat     = geo.get("lat"),
        geo_lon     = geo.get("lon"),
    )
    db.add(entry)
    db.flush()   # get entry.id without full commit

    # ── Suppression check (Feature 7) ─────────────────────────────────────────
    if _is_suppressed(db, ip, message):
        log.debug("Suppressed log line from %s", ip)
        db.commit()
        return entry

    # ── Rule matching ─────────────────────────────────────────────────────────
    matched_rules: list[Rule] = []
    for rule in RULES:
        for pattern in rule.patterns:
            if pattern.search(message):
                matched_rules.append(rule)
                entry.severity   = rule.severity
                entry.event_type = rule.event_type
                break

    # ── Brute-force heuristic (Bug Fix #3 — use log-event timestamp) ──────────
    is_failed = any(
        r.event_type in ("failed_login", "ssh_auth_failure") for r in matched_rules
    )
    event_ts_float = parsed["timestamp"].timestamp()
    if is_failed and _check_brute_force(ip, event_ts_float):
        from app.detector.rules import Rule as _Rule
        import re as _re
        bf_rule = _Rule(
            name="Brute Force (heuristic)",
            severity="CRITICAL",
            event_type="brute_force",
            patterns=[],
        )
        matched_rules.append(bf_rule)
        entry.severity   = "CRITICAL"
        entry.event_type = "brute_force"

    # ── Create alerts ─────────────────────────────────────────────────────────
    for rule in matched_rules:
        alert = Alert(
            alert_type   = rule.event_type,
            severity     = rule.severity,
            source_ip    = ip,
            message      = f"{rule.name}: {message[:500]}",
            log_entry_id = entry.id,
        )
        db.add(alert)

        # Feature 1 — email on CRITICAL
        if rule.severity == "CRITICAL":
            try:
                from app.utils.email_sender import send_critical_alert_email
                send_critical_alert_email(rule.name, ip or "", message)
            except Exception as exc:
                log.warning("Alert email failed: %s", exc)

    db.commit()
    db.refresh(entry)
    return entry
