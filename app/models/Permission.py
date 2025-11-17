from app.db.base import Base
from sqlalchemy import Column, BigInteger, String, Text
from sqlalchemy.orm import relationship

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")