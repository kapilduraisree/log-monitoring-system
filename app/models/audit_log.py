"""AuditLog ORM model — Feature 4: User Activity Audit Log."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database.engine import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id          = Column(Integer,  primary_key=True, index=True)
    created_at  = Column(DateTime, default=datetime.utcnow, index=True)
    user_id     = Column(Integer,  ForeignKey("users.id"), nullable=True)
    username    = Column(String(64), nullable=True)
    action      = Column(String(128), nullable=False)   # e.g. "LOGIN", "DELETE_LOG", "ACK_ALERT"
    resource    = Column(String(256), nullable=True)    # e.g. "/logs/42"
    detail      = Column(Text,        nullable=True)
    ip_address  = Column(String(64),  nullable=True)
