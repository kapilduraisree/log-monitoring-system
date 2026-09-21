"""Feature 5: Scheduled report emailer using asyncio background task."""

import asyncio
from datetime import datetime, timezone

from app.utils.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

_task: asyncio.Task | None = None


async def _scheduler_loop():
    log.info("Scheduled report task started (hour=%d UTC)", settings.REPORT_SCHEDULE_HOUR)
    last_sent_day: int = -1
    while True:
        now = datetime.now(timezone.utc)
        if now.hour == settings.REPORT_SCHEDULE_HOUR and now.day != last_sent_day:
            log.info("Sending scheduled daily report…")
            try:
                from app.database.engine import SessionLocal
                from app.services.report_service import send_scheduled_report
                db = SessionLocal()
                try:
                    send_scheduled_report(db, "daily")
                finally:
                    db.close()
                last_sent_day = now.day
            except Exception as exc:
                log.error("Scheduled report failed: %s", exc)
        await asyncio.sleep(60)   # check every minute


def start_scheduler():
    global _task
    if not settings.REPORT_SCHEDULE_ENABLED:
        return
    if _task is None or _task.done():
        loop = asyncio.get_event_loop()
        _task = loop.create_task(_scheduler_loop())
        log.info("Report scheduler started.")


def stop_scheduler():
    global _task
    if _task and not _task.done():
        _task.cancel()
        _task = None
