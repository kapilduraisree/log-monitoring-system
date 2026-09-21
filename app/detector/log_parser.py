"""Parse raw log lines into structured dicts."""

import re
from datetime import datetime, timezone
from typing import Optional

from app.utils.helpers import extract_ip

# ── Timestamp patterns ────────────────────────────────────────────────────────
_ISO_RE   = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?")
_SYSLOG_RE = re.compile(r"[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}")
_APACHE_RE = re.compile(r"\d{2}/[A-Z][a-z]{2}/\d{4}:\d{2}:\d{2}:\d{2}\s[+-]\d{4}")

_SEVERITY_RE = re.compile(
    r"\b(CRITICAL|HIGH|MEDIUM|LOW|INFO|ERROR|WARN(?:ING)?|DEBUG|ALERT|EMERG|NOTICE)\b",
    re.IGNORECASE,
)

_SEVERITY_MAP = {
    "CRITICAL": "CRITICAL", "EMERG": "CRITICAL", "ALERT": "CRITICAL",
    "HIGH": "HIGH", "ERROR": "HIGH",
    "MEDIUM": "MEDIUM", "WARN": "MEDIUM", "WARNING": "MEDIUM",
    "LOW": "LOW", "NOTICE": "LOW",
    "INFO": "INFO", "DEBUG": "INFO",
}


def _parse_iso_ts(s: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_syslog_ts(s: str) -> Optional[datetime]:
    try:
        dt = datetime.strptime(s, "%b %d %H:%M:%S")
        return dt.replace(year=datetime.utcnow().year, tzinfo=timezone.utc)
    except ValueError:
        return None


def _parse_apache_ts(s: str) -> Optional[datetime]:
    try:
        return datetime.strptime(s, "%d/%b/%Y:%H:%M:%S %z")
    except ValueError:
        return None


def parse_line(raw: str, source_file: str = "") -> dict:
    """Return a dict with keys: timestamp, source_ip, severity, message, raw_line, source_file."""
    line = raw.strip()

    # ── Timestamp ─────────────────────────────────────────────────────────────
    timestamp = None
    for regex, parser in [
        (_ISO_RE, _parse_iso_ts),
        (_APACHE_RE, _parse_apache_ts),
        (_SYSLOG_RE, _parse_syslog_ts),
    ]:
        m = regex.search(line)
        if m:
            timestamp = parser(m.group())
            if timestamp:
                break
    if timestamp is None:
        timestamp = datetime.utcnow().replace(tzinfo=timezone.utc)

    # ── Severity ──────────────────────────────────────────────────────────────
    severity = "INFO"
    sm = _SEVERITY_RE.search(line)
    if sm:
        severity = _SEVERITY_MAP.get(sm.group().upper(), "INFO")

    # ── Source IP ─────────────────────────────────────────────────────────────
    source_ip = extract_ip(line)

    return {
        "timestamp":   timestamp,
        "source_ip":   source_ip,
        "severity":    severity,
        "message":     line[:2000],
        "raw_line":    line[:4000],
        "source_file": source_file,
    }
