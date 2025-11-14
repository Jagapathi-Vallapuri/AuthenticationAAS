from pydantic import BaseModel
from typing import List


class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    id: int

    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    user_id: int
    role_id: int
