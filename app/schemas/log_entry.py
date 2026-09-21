from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LogEntryOut(BaseModel):
    id: int
    timestamp: datetime
    source_file: Optional[str]
    source_ip: Optional[str]
    severity: str
    event_type: Optional[str]
    message: str
    raw_line: Optional[str]
    geo_country: Optional[str]
    geo_city: Optional[str]
    geo_lat: Optional[float]
    geo_lon: Optional[float]

    model_config = {"from_attributes": True}


class LogsPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[LogEntryOut]
