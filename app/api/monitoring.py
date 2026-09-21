"""
Monitoring routes — start/stop/status, file upload.
Feature 8: Multi-target endpoints (add/remove/list targets).
"""

import os
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session

from app.database.engine import get_db
from app.schemas.monitor import MonitorStartRequest, MonitorTargetCreate, MonitorTargetOut
from app.services import monitor_service
from app.services.audit_service import record as audit
from app.models.monitor_target import MonitorTarget
from app.api.deps import require_admin, get_current_user, get_client_ip
from app.utils.config import settings
from app.utils.logger import get_logger
from app.models.user import User

router = APIRouter(tags=["monitoring"])
log = get_logger(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Single-path start/stop (original API) ─────────────────────────────────────

@router.post("/monitor/start")
def start_monitor(
    body: MonitorStartRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    ok = monitor_service.start_monitoring(body.watch_path, body.alert_threshold or settings.ALERT_THRESHOLD)
    audit(db, "MONITOR_START", admin.id, admin.username,
          body.watch_path, ip_address=get_client_ip(request))
    return {"started": ok, "path": body.watch_path}


@router.post("/monitor/stop")
def stop_monitor(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    stopped = monitor_service.stop_monitoring()
    audit(db, "MONITOR_STOP", admin.id, admin.username,
          ip_address=get_client_ip(request))
    return {"stopped": stopped}


@router.get("/monitor/status")
def monitor_status(_: User = Depends(get_current_user)):
    return monitor_service.monitoring_status()


# ── Feature 8: Multi-target management ───────────────────────────────────────

@router.get("/monitor/targets", response_model=list[MonitorTargetOut])
def list_targets(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(MonitorTarget).all()


@router.post("/monitor/targets", response_model=MonitorTargetOut, status_code=201)
def add_target(
    body: MonitorTargetCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    existing = db.query(MonitorTarget).filter(MonitorTarget.path == body.path).first()
    if existing:
        raise HTTPException(400, "Target already registered")
    target = MonitorTarget(path=body.path, label=body.label, is_active=True, added_by=admin.id)
    db.add(target)
    db.commit()
    db.refresh(target)
    # Start watching immediately
    monitor_service.start_monitoring(body.path, settings.ALERT_THRESHOLD)
    audit(db, "ADD_MONITOR_TARGET", admin.id, admin.username,
          body.path, ip_address=get_client_ip(request))
    return target


@router.delete("/monitor/targets/{target_id}")
def remove_target(
    target_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    target = db.query(MonitorTarget).filter(MonitorTarget.id == target_id).first()
    if not target:
        raise HTTPException(404, "Target not found")
    monitor_service.stop_monitoring(target.path)
    db.delete(target)
    db.commit()
    audit(db, "REMOVE_MONITOR_TARGET", admin.id, admin.username,
          target.path, ip_address=get_client_ip(request))
    return {"detail": "Removed"}


# ── File upload ───────────────────────────────────────────────────────────────

@router.post("/upload-log")
async def upload_log(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    dest_path = os.path.join(UPLOAD_DIR, file.filename)

    written = 0
    with open(dest_path, "wb") as out:
        while True:
            chunk = await file.read(65536)
            if not chunk:
                break
            written += len(chunk)
            if written > max_bytes:
                os.remove(dest_path)
                raise HTTPException(413, f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit")
            out.write(chunk)

    # Process the uploaded file
    from app.detector.engine import process_line
    lines_processed = 0
    with open(dest_path, "rb") as f:
        for raw in f:
            line = raw.decode("utf-8", errors="replace").strip()
            if line:
                process_line(line, dest_path, db)
                lines_processed += 1

    audit(db, "UPLOAD_LOG", current_user.id, current_user.username,
          dest_path, detail=f"{lines_processed} lines",
          ip_address=get_client_ip(request))
    return {"filename": file.filename, "lines_processed": lines_processed}
