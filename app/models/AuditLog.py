from sqlalchemy import BigInteger, Column, DateTime, Text, ForeignKey, Enum, func
from app.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, INET
from .AuditAction import AuditAction

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    action_type = Column(Enum(AuditAction, name= "audit_action_enum"), nullable=False)
    metadata_ = Column("metadata", JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")