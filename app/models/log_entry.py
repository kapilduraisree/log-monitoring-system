"""LogEntry ORM model — stores every parsed log event."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database.engine import Base


class LogEntry(Base):
    __tablename__ = "log_entries"

    id           = Column(Integer, primary_key=True, index=True)
    timestamp    = Column(DateTime, default=datetime.utcnow, index=True)
    source_file  = Column(String(256), nullable=True)
    source_ip    = Column(String(64),  nullable=True, index=True)
    severity     = Column(String(16),  default="INFO", index=True)   # CRITICAL/HIGH/MEDIUM/LOW/INFO
    event_type   = Column(String(64),  nullable=True, index=True)
    message      = Column(Text,        nullable=False)
    raw_line     = Column(Text,        nullable=True)

    # ── Feature 2: IP Geolocation ─────────────────────────────────────────────
    geo_country  = Column(String(64),  nullable=True)
    geo_city     = Column(String(64),  nullable=True)
    geo_lat      = Column(Float,       nullable=True)
    geo_lon      = Column(Float,       nullable=True)
