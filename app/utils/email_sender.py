"""Feature 1 + 5: Email sending utilities (SMTP with TLS)."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional

from app.utils.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)


def _build_recipients(override: Optional[str] = None) -> list[str]:
    raw = override or settings.EMAIL_TO
    return [r.strip() for r in raw.split(",") if r.strip()]


def send_email(
    subject: str,
    body_html: str,
    recipients: Optional[list[str]] = None,
    attachment_bytes: Optional[bytes] = None,
    attachment_filename: Optional[str] = None,
) -> bool:
    """Send an HTML email.  Returns True on success."""
    if not settings.EMAIL_HOST:
        log.warning("EMAIL_HOST not configured — skipping email send.")
        return False

    to_list = recipients or _build_recipients()
    if not to_list:
        log.warning("No email recipients configured.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM or settings.EMAIL_USER
    msg["To"] = ", ".join(to_list)

    msg.attach(MIMEText(body_html, "html"))

    if attachment_bytes and attachment_filename:
        part = MIMEApplication(attachment_bytes, Name=attachment_filename)
        part["Content-Disposition"] = f'attachment; filename="{attachment_filename}"'
        msg.attach(part)

    try:
        if settings.EMAIL_USE_TLS:
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                if settings.EMAIL_USER:
                    server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
                server.sendmail(msg["From"], to_list, msg.as_string())
        else:
            with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                if settings.EMAIL_USER:
                    server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
                server.sendmail(msg["From"], to_list, msg.as_string())
        log.info("Email sent: %s → %s", subject, to_list)
        return True
    except Exception as exc:
        log.error("Failed to send email: %s", exc)
        return False


def send_critical_alert_email(alert_type: str, source_ip: str, message: str) -> bool:
    """Feature 1 — send a CRITICAL alert notification email."""
    subject = f"🚨 CRITICAL Security Alert: {alert_type}"
    body = f"""
    <html><body style="font-family:monospace;background:#0f172a;color:#f8fafc;padding:24px;">
      <h2 style="color:#ef4444;">🚨 CRITICAL Alert Detected</h2>
      <table style="border-collapse:collapse;width:100%;">
        <tr><td style="padding:8px;color:#94a3b8;">Alert Type</td><td style="padding:8px;color:#f8fafc;">{alert_type}</td></tr>
        <tr><td style="padding:8px;color:#94a3b8;">Source IP</td><td style="padding:8px;color:#fbbf24;">{source_ip or 'N/A'}</td></tr>
        <tr><td style="padding:8px;color:#94a3b8;">Message</td><td style="padding:8px;color:#f8fafc;">{message}</td></tr>
      </table>
      <p style="color:#64748b;margin-top:24px;">Log Security Monitoring System</p>
    </body></html>
    """
    return send_email(subject, body)
