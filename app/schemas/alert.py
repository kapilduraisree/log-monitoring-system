from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AlertOut(BaseModel):
    id: int
    created_at: datetime
    alert_type: str
    severity: str
    source_ip: Optional[str]
    message: str
    log_entry_id: Optional[int]
    acknowledged: bool
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[int]
    ack_note: Optional[str]

    model_config = {"from_attributes": True}


class AlertsPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AlertOut]


class AckRequest(BaseModel):
    note: Optional[str] = None
