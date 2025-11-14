from __future__ import annotations
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.User import User
from app.schemas.user import UserUpdate
from app.services.auth_service import hash_password

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    return await db.get(User, user_id)

async def get_user_by_email(db: AsyncSession, email:str) -> Optional[User]:
    res = await db.execute(select(User). where(User.email == email))
    return res.scalar_one_or_none()

async def list_users(db: AsyncSession) -> List[User]:
    res = await db.execute(select(User).order_by(User.id))
    return list(res.scalars().all())

async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = False #type: ignore
    await db.flush()

    return True

async def activate_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = True #type: ignore
    await db.flush()

    return True

async def update_user(
    db: AsyncSession, 
    user: User, 
    data: UserUpdate
) -> User:

    if data.email is not None:
        user.email = data.email #type:ignore 

    if data.password is not None:
        user.password_hash = hash_password(data.password) #type: ignore

    if data.is_active is not None:
        user.is_active = data.is_active #type: ignore

    await db.flush()
    await db.refresh(user)
    return user

async def hard_delete_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)

    if not user:
        return False
    
    await db.delete(user)
    await db.flush()

    return True

async def require_user(db: AsyncSession, user_id: int) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")
    
    return user