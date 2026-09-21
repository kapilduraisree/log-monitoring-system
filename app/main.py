"""
FastAPI application entry point.

Bug Fix #6: /ws registered directly on app (not under /api/v1 prefix)
to match the Vite proxy config.
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.utils.config import settings
from app.utils.logger import get_logger
from app.database.init_db import init_db
from app.services.websocket_service import ws_endpoint
from app.services.scheduler_service import start_scheduler

from app.api import auth, logs, alerts, reports, monitoring, suppression, audit

log = get_logger(__name__)

app = FastAPI(
    title="Log Security Monitoring System",
    version="2.0.0",
    description="Real-time security log monitoring with 10 enhanced features.",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routes under /api/v1 ──────────────────────────────────────────────────
PREFIX = "/api/v1"
app.include_router(auth.router,        prefix=PREFIX)
app.include_router(logs.router,        prefix=PREFIX)
app.include_router(alerts.router,      prefix=PREFIX)
app.include_router(reports.router,     prefix=PREFIX)
app.include_router(monitoring.router,  prefix=PREFIX)
app.include_router(suppression.router, prefix=PREFIX)
app.include_router(audit.router,       prefix=PREFIX)

# ── Bug Fix #6: WebSocket at /ws (no /api/v1 prefix) ─────────────────────────
@app.websocket("/ws")
async def websocket_route(ws: WebSocket):
    await ws_endpoint(ws)


# ── Startup / shutdown ────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    log.info("Initialising database…")
    init_db()
    log.info("Starting report scheduler…")
    start_scheduler()
    log.info("✅  Log Security Monitoring System v2.0 ready.")


@app.on_event("shutdown")
async def on_shutdown():
    from app.services.monitor_service import stop_monitoring
    from app.services.scheduler_service import stop_scheduler
    stop_monitoring()
    stop_scheduler()
    log.info("Shutdown complete.")


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
