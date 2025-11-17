from app.db.base import Base
from sqlalchemy import Column, BigInteger, ForeignKey

class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(BigInteger, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)