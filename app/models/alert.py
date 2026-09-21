"""Alert ORM model — includes acknowledgement fields (Feature 3)."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from app.database.engine import Base


class Alert(Base):
    __tablename__ = "alerts"

    id             = Column(Integer, primary_key=True, index=True)
    created_at     = Column(DateTime, default=datetime.utcnow, index=True)
    alert_type     = Column(String(64),  nullable=False, index=True)
    severity       = Column(String(16),  default="HIGH", index=True)
    source_ip      = Column(String(64),  nullable=True)
    message        = Column(Text,        nullable=False)
    log_entry_id   = Column(Integer,     nullable=True)

    # ── Feature 3: Alert Acknowledgement ──────────────────────────────────────
    acknowledged      = Column(Boolean,      default=False, index=True)
    acknowledged_at   = Column(DateTime,     nullable=True)
    acknowledged_by   = Column(Integer,      ForeignKey("users.id"), nullable=True)
    ack_note          = Column(Text,         nullable=True)
