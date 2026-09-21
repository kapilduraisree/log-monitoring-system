"""
Monitor service — Watchdog file-system event handler.
Feature 8: Multi-target monitoring (multiple paths).
Bug Fix #4: Opens files in binary mode "rb" to avoid Windows CRLF corruption.
"""

import os
import threading
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from app.utils.logger import get_logger

log = get_logger(__name__)

_observers: dict[str, Observer] = {}   # path → observer
_lock = threading.Lock()


class LogFileHandler(FileSystemEventHandler):
    def __init__(self, watch_path: str, alert_threshold: int = 5):
        super().__init__()
        self.watch_path      = watch_path
        self.alert_threshold = alert_threshold
        self._offsets: dict[str, int] = {}

    def on_modified(self, event):
        if event.is_directory:
            return
        path = event.src_path
        self._tail(path)

    def _tail(self, filepath: str):
        # Bug Fix #4 — open in binary mode to avoid Windows \r\n corruption
        try:
            offset = self._offsets.get(filepath, 0)
            with open(filepath, "rb") as f:
                f.seek(offset)
                new_data = f.read()
                self._offsets[filepath] = f.tell()

            if not new_data:
                return

            from app.database.engine import SessionLocal
            from app.detector.engine import process_line

            lines = new_data.decode("utf-8", errors="replace").splitlines()
            db = SessionLocal()
            try:
                for line in lines:
                    if line.strip():
                        entry = process_line(line, filepath, db)
                        if entry:
                            from app.services.websocket_service import broadcast_alert
                            import asyncio
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    loop.create_task(broadcast_alert({
                                        "id":         entry.id,
                                        "severity":   entry.severity,
                                        "event_type": entry.event_type,
                                        "source_ip":  entry.source_ip,
                                        "message":    entry.message[:200],
                                        "timestamp":  entry.timestamp.isoformat() + "Z",
                                    }))
                            except Exception:
                                pass
            finally:
                db.close()
        except Exception as exc:
            log.error("Tail error on %s: %s", filepath, exc)


def start_monitoring(watch_path: str, alert_threshold: int = 5) -> bool:
    """Start watching *watch_path*. Returns False if already watching."""
    with _lock:
        if watch_path in _observers:
            return False
        if not os.path.exists(watch_path):
            os.makedirs(watch_path, exist_ok=True)
        handler  = LogFileHandler(watch_path, alert_threshold)
        observer = Observer()
        observer.schedule(handler, watch_path, recursive=False)
        observer.start()
        _observers[watch_path] = observer
        log.info("Started monitoring: %s", watch_path)
        return True


def stop_monitoring(watch_path: Optional[str] = None) -> int:
    """
    Stop monitoring *watch_path* (or all paths if None).
    Returns number of observers stopped.
    """
    with _lock:
        targets = [watch_path] if watch_path else list(_observers.keys())
        stopped = 0
        for p in targets:
            obs = _observers.pop(p, None)
            if obs:
                obs.stop()
                obs.join()
                stopped += 1
                log.info("Stopped monitoring: %s", p)
        return stopped


def monitoring_status() -> dict:
    with _lock:
        return {
            "active": len(_observers) > 0,
            "targets": list(_observers.keys()),
            "count": len(_observers),
        }
