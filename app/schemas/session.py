from pydantic import BaseModel
from datetime import datetime


class SessionRead(BaseModel):
    id: int
    device_info: str | None
    ip_address: str | None
    last_used_at: datetime
    revoked: bool

    class Config:
        from_attributes = True
        orm_mode = True