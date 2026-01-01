from __future__ import annotations
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.schemas.role import RoleCreate 
from app.models.Role import Role
from app.models.User import User
from app.models.Permission import Permission
from app.models.UserRole import UserRole
from app.schemas.permission import PermissionBase
from app.models.RolePermission import RolePermission


async def create_role(db: AsyncSession, data: RoleCreate) -> Role:
    res = await db.execute(select(Role).where(Role.name == data.name))
    existing = res.scalar_one_or_none()

    if existing:
        raise ValueError("Role already exists")
    
    role = Role(name=data.name, description= data.description)
    db.add(role)

    await db.flush()
    await db.refresh(role)

    return role

async def get_role_by_id(db: AsyncSession, role_id: int) -> Optional[Role]:
    return await db.get(Role, role_id)

async def get_role_by_name(db: AsyncSession, name: str) -> Optional[Role]:
    res = await db.execute(select(Role).where(Role.name == name))
    return res.scalar_one_or_none()

async def list_roles(db: AsyncSession) -> List[Role]:
    result = await db.execute(select(Role).order_by(Role.id))
    return list(result.scalars().all())


async def delete_role(db: AsyncSession, role_id: int) -> bool:
    role = await get_role_by_id(db, role_id)
    if not role:
        return False

    await db.delete(role)
    await db.flush()
    return True


async def remove_role_from_user(db: AsyncSession, user: User, role: Role) -> bool:
    res = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id
        )
    )

    existing = res.scalar_one_or_none()

    if not existing:
        return False

    await db.delete(existing)
    await db.flush()
    return True

async def get_user_roles(db: AsyncSession, user_id: int) -> List[Role]:
    res = await db.execute(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
    )

    return list(res.scalars().all())

async def create_permission(db: AsyncSession, data: PermissionBase) -> Permission:
    res = await db.execute(select(Permission).where(Permission.name == data.name))
    existing = res.scalar_one_or_none()

    if existing:
        raise ValueError("Permission already exists")
    
    perm = Permission(name=data.name, description=data.description)
    db.add(perm)

    await db.flush()
    await db.refresh(perm)

    return perm

async def get_permission_by_id(db: AsyncSession, perm_id: int) -> Optional[Permission]:
    return await db.get(Permission, perm_id)

async def list_permissions(db: AsyncSession) -> List[Permission]:
    result = await db.execute(select(Permission).order_by(Permission.id))
    return list(result.scalars().all())

async def assign_permission_to_role(db: AsyncSession, role: Role, perm: Permission) -> bool:
    res = await db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == perm.id
        )
    )

    existing = res.scalar_one_or_none()
    if existing:
        return False
    
    link = RolePermission(role_id=role.id, permission_id=perm.id)
    db.add(link)

    await db.flush()
    return True

async def assign_role_to_user(db: AsyncSession, user: User, role:Role ):

    res = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id
        )
    )
    existing = res.scalar_one_or_none()
    if existing:
        return False
    
    link = UserRole(user_id = user.id, role_id=role.id)
    db.add(link)
    await db.flush()
    return True

async def remove_permission_from_role(db: AsyncSession, role:Role, perm: Permission) -> bool:

    res = await db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == perm.id
        )
    )

    row = res.scalar_one_or_none()
    if not row:
        return False
    
    await db.delete(row)
    await db.flush()

    return True

async def get_role_permissions(db: AsyncSession, role_id: int) -> List[Permission]:
    result = await db.execute(
        select(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == role_id)
    )
    return list(result.scalars().all())

async def get_user_permissions(db: AsyncSession, user_id: int) -> List[str]:
    roles = await get_user_roles(db, user_id)

    if not roles:
        return []
    
    perm_names = set()

    for role in roles:
        perms = await get_role_permissions(db, role.id) #type: ignore
        for p in perms:
            perm_names.add(p.name)
    
    return list(perm_names)