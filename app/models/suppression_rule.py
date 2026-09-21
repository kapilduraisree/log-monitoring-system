"""SuppressionRule ORM model — Feature 7: Alert Suppression / Whitelist."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from app.database.engine import Base


class SuppressionRule(Base):
    __tablename__ = "suppression_rules"

    id          = Column(Integer,  primary_key=True, index=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    rule_type   = Column(String(16), nullable=False)    # "ip" | "pattern"
    value       = Column(String(256), nullable=False)   # IP or regex pattern
    reason      = Column(Text, nullable=True)
    is_active   = Column(Boolean, default=True)
    created_by  = Column(Integer, nullable=True)
