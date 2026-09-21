from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AuditLogOut(BaseModel):
    id: int
    created_at: datetime
    user_id: Optional[int]
    username: Optional[str]
    action: str
    resource: Optional[str]
    detail: Optional[str]
    ip_address: Optional[str]

    model_config = {"from_attributes": True}


class AuditLogsPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AuditLogOut]
