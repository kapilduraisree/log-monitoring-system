"""MonitorTarget ORM model — Feature 8: Multi-file/directory monitoring."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database.engine import Base


class MonitorTarget(Base):
    __tablename__ = "monitor_targets"

    id          = Column(Integer,  primary_key=True, index=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    path        = Column(String(512), nullable=False, unique=True)
    label       = Column(String(128), nullable=True)
    is_active   = Column(Boolean, default=True)
    added_by    = Column(Integer, nullable=True)
