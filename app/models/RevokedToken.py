from db.base import Base
from sqlalchemy import Column, String, DateTime, func

class RevokedToken(Base):
    jti = Column(String, primary_key=True)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())