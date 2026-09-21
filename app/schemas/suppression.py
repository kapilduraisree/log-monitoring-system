from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SuppressionRuleCreate(BaseModel):
    rule_type: str   # "ip" | "pattern"
    value: str
    reason: Optional[str] = None


class SuppressionRuleOut(BaseModel):
    id: int
    created_at: datetime
    rule_type: str
    value: str
    reason: Optional[str]
    is_active: bool
    created_by: Optional[int]

    model_config = {"from_attributes": True}
