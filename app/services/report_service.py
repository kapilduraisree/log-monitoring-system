"""
Report service — daily/weekly/monthly summaries, PDF/CSV/JSON export.
Feature 5: Scheduled report email integrated here.
"""

import csv
import io
import json
from datetime import datetime, timedelta
from typing import Literal

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.models.log_entry import LogEntry
from app.models.alert import Alert
from app.utils.logger import get_logger

log = get_logger(__name__)

Period = Literal["daily", "weekly", "monthly"]

_PERIOD_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}


def _since(period: Period) -> datetime:
    return datetime.utcnow() - timedelta(days=_PERIOD_DAYS[period])


def build_report(db: Session, period: Period) -> dict:
    since = _since(period)

    sev_counts = (
        db.query(LogEntry.severity, func.count(LogEntry.id))
        .filter(LogEntry.timestamp >= since)
        .group_by(LogEntry.severity)
        .all()
    )
    sev_map = {s: 0 for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")}
    for s, c in sev_counts:
        if s in sev_map:
            sev_map[s] = c

    top_types = (
        db.query(LogEntry.event_type, func.count(LogEntry.id).label("c"))
        .filter(LogEntry.timestamp >= since, LogEntry.event_type != None)  # noqa: E711
        .group_by(LogEntry.event_type)
        .order_by(desc("c"))
        .limit(10)
        .all()
    )
    top_ips = (
        db.query(LogEntry.source_ip, func.count(LogEntry.id).label("c"))
        .filter(LogEntry.timestamp >= since, LogEntry.source_ip != None)  # noqa: E711
        .group_by(LogEntry.source_ip)
        .order_by(desc("c"))
        .limit(10)
        .all()
    )
    total_alerts = (
        db.query(func.count(Alert.id))
        .filter(Alert.created_at >= since)
        .scalar()
        or 0
    )

    return {
        "period":       period,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "since":        since.isoformat() + "Z",
        "severity":     sev_map,
        "total_logs":   sum(sev_map.values()),
        "total_alerts": total_alerts,
        "top_event_types": [{"type": r.event_type, "count": r.c} for r in top_types],
        "top_source_ips":  [{"ip": r.source_ip,   "count": r.c} for r in top_ips],
    }


def export_csv(db: Session, period: Period) -> bytes:
    report = build_report(db, period)
    since = _since(period)
    rows = (
        db.query(LogEntry)
        .filter(LogEntry.timestamp >= since)
        .order_by(desc(LogEntry.timestamp))
        .limit(5000)
        .all()
    )
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "timestamp", "severity", "event_type", "source_ip", "geo_country", "geo_city", "message"])
    for r in rows:
        writer.writerow([r.id, r.timestamp, r.severity, r.event_type, r.source_ip, r.geo_country, r.geo_city, r.message])
    return buf.getvalue().encode()


def export_json(db: Session, period: Period) -> bytes:
    report = build_report(db, period)
    return json.dumps(report, indent=2).encode()


def export_pdf(db: Session, period: Period) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors

    report = build_report(db, period)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Security Report — {period.capitalize()}", styles["Title"]))
    story.append(Paragraph(f"Generated: {report['generated_at']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Severity table
    story.append(Paragraph("Severity Breakdown", styles["Heading2"]))
    sev_data = [["Severity", "Count"]] + [[k, v] for k, v in report["severity"].items()]
    t = Table(sev_data, colWidths=[200, 100])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.HexColor("#e2e8f0")]),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Top event types
    story.append(Paragraph("Top Event Types", styles["Heading2"]))
    te_data = [["Event Type", "Count"]] + [[r["type"], r["count"]] for r in report["top_event_types"]]
    t2 = Table(te_data, colWidths=[300, 100])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(t2)
    story.append(Spacer(1, 12))

    # Top IPs
    story.append(Paragraph("Top Attacker IPs", styles["Heading2"]))
    ip_data = [["IP Address", "Count"]] + [[r["ip"], r["count"]] for r in report["top_source_ips"]]
    t3 = Table(ip_data, colWidths=[300, 100])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(t3)

    doc.build(story)
    return buf.getvalue()


# ── Feature 5: Scheduled report email ─────────────────────────────────────────

def send_scheduled_report(db: Session, period: Period = "daily") -> bool:
    from app.utils.email_sender import send_email
    from app.utils.config import settings

    report = build_report(db, period)
    pdf_bytes = export_pdf(db, period)
    recipients = [r.strip() for r in (settings.REPORT_EMAIL_TO or settings.EMAIL_TO).split(",") if r.strip()]

    subject = f"📊 {period.capitalize()} Security Report — {datetime.utcnow().strftime('%Y-%m-%d')}"
    body = f"""
    <html><body style="font-family:sans-serif;background:#0f172a;color:#f8fafc;padding:24px;">
      <h2>Security Report — {period.capitalize()}</h2>
      <p>Period: {report['since']} → {report['generated_at']}</p>
      <ul>
        <li>Total logs: <strong>{report['total_logs']}</strong></li>
        <li>Total alerts: <strong>{report['total_alerts']}</strong></li>
        <li>Critical: <strong>{report['severity'].get('CRITICAL', 0)}</strong></li>
        <li>High: <strong>{report['severity'].get('HIGH', 0)}</strong></li>
      </ul>
      <p>See the attached PDF for full details.</p>
    </body></html>
    """
    return send_email(
        subject=subject,
        body_html=body,
        recipients=recipients,
        attachment_bytes=pdf_bytes,
        attachment_filename=f"security_report_{period}_{datetime.utcnow().strftime('%Y%m%d')}.pdf",
    )
