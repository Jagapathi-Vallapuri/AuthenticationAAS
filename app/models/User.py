from db.base import Base
from sqlalchemy import BigInteger, Boolean, Column, String, Integer, DateTime, Index, Text, func
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    email = Column(CITEXT, unique=True, nullable=False)
    password_hash = Column(Text, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    

    roles = relationship("Role", secondary = "user_roles", back_populates="users")
    