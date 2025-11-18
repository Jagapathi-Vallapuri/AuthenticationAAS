from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    refresh_token_id = Column(BigInteger, ForeignKey("refresh_tokens.id", ondelete="CASCADE"), unique=True)
    device_info = Column(Text)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="sessions")
    refresh_token = relationship("RefreshToken", back_populates="session")

    @property
    def ip_address(self) -> str | None:
        if self.refresh_token.ip_address and self.refresh_token is not None:
            return str(self.refresh_token.ip_address)
        return None