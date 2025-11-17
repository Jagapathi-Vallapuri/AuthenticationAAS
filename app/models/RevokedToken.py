from app.db.base import Base
from sqlalchemy import Column, String, DateTime, func

class RevokedToken(Base):
    __tablename__ = 'revoked_tokens'
    jti = Column(String, primary_key=True)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())