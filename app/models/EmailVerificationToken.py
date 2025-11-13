from sqlalchemy import Column, BigInteger, ForeignKey, Boolean, DateTime, Text, func
from sqlalchemy.orm import relationship
from db.base import Base

class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    token_hash = Column(Text, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="email_tokens")