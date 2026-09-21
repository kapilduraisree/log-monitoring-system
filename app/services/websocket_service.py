"""
WebSocket connection manager.
Bug Fix #5: try/finally ensures socket cleanup on disconnect.
"""

import asyncio
import json
from typing import Any

from fastapi import WebSocket
from app.utils.logger import get_logger

log = get_logger(__name__)

_connections: set[WebSocket] = set()


async def connect(ws: WebSocket):
    await ws.accept()
    _connections.add(ws)
    log.info("WS client connected. Total: %d", len(_connections))


def disconnect(ws: WebSocket):
    _connections.discard(ws)
    log.info("WS client disconnected. Total: %d", len(_connections))


async def broadcast_alert(data: dict[str, Any]):
    if not _connections:
        return
    payload = json.dumps(data)
    dead: list[WebSocket] = []
    for ws in list(_connections):
        try:
            await ws.send_text(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections.discard(ws)


async def ws_endpoint(ws: WebSocket):
    """Bug Fix #5 — try/finally guarantees cleanup."""
    await connect(ws)
    try:
        while True:
            # Keep alive — client can send pings
            await ws.receive_text()
    except Exception:
        pass
    finally:
        disconnect(ws)
