from pydantic import BaseModel
from typing import Optional


class MonitorStartRequest(BaseModel):
    watch_path: str
    alert_threshold: Optional[int] = 5


class MonitorTargetCreate(BaseModel):
    path: str
    label: Optional[str] = None


class MonitorTargetOut(BaseModel):
    id: int
    path: str
    label: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}
