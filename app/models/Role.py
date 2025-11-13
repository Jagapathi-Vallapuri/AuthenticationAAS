from db.base import Base
from sqlalchemy import Column, String, BigInteger, Text
from sqlalchemy.orm import relationship

class Role(Base):
    __tablename__ = 'roles'
    id = Column(BigInteger, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
