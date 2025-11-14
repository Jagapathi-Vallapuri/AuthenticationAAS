from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    is_active: bool

    class Config:
        from_attributes = True

class UserAdminRead(UserRead):
    roles: List[str] = []