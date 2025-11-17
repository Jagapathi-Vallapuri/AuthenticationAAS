from app.db.base import Base
from sqlalchemy import Column, BigInteger, ForeignKey, Text, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import INET

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    token_hash = Column(Text, nullable=False)
    user_agent = Column(Text)
    ip_address = Column(INET)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens")
    session = relationship("Session", back_populates="refresh_token", uselist=False)