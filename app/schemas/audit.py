from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AuditLogRead(BaseModel):
    id: int
    action_type: str
    metadata: dict | None
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
