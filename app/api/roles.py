from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.role import RoleRead, RoleCreate, AssignRoleRequest
from app.schemas.permission import PermissionBase, PermissionRead
from app.models.AuditAction import  AuditAction
from app.core.security import require_roles
from app.services import role_service, audit_service, user_service

router = APIRouter(tags=['Roles & Permissions'])

@router.post('/', response_model=RoleRead)
async def create_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_roles('admin'))
):
    try:
        role = await role_service.create_role(db, data)
        await db.commit()

        await audit_service.log_action(
            db, 
            user_id=admin.id,
            action_type=AuditAction.ROLE_CREATED,
            metadata={'role': data.name}
        )

        await db.commit()
    except ValueError as e:
        raise HTTPException(400, str(e))

    return role

@router.get('/', response_model=List[RoleRead])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_roles('admin'))
):
    roles = await role_service.list_roles(db)
    return roles


@router.get('/{role_id}', response_model=RoleRead)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_roles('admin'))
):
    role = await role_service.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(404, 'Role not found')
    return role

@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_roles("admin")),
):
    ok = await role_service.delete_role(db, role_id)
    if not ok:
        raise HTTPException(404, "Role not found")
    await db.commit()

    await audit_service.log_action(
        db,
        user_id=admin.id,
        action_type=AuditAction.ROLE_DELETED,
        metadata={"role_id": role_id},
    )
    await db.commit()

    return {"message": "Role deleted"}


@router.post("/{role_id}/assign/{user_id}")
async def assign_role(
    role_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_roles("admin"))
):
    role = await role_service.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(404, "Role not found")

    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    await role_service.assign_role_to_user(db, user, role)
    await db.commit()

    await audit_service.log_action(
        db,
        user_id=admin.id,
        action_type=AuditAction.ROLE_ASSIGNED,
        metadata={"role_id": role_id, "target_user": user_id},
    )
    await db.commit()

    return {"message": "Role assigned"}

@router.delete("/{role_id}/assign/{user_id}")
async def remove_role(
    role_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_roles("admin"))
):
    role = await role_service.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(404, "Role not found")

    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    await role_service.remove_role_from_user(db, user, role)
    await db.commit()

    await audit_service.log_action(
        db,
        user_id=admin.id,
        action_type=AuditAction.ROLE_REMOVED,
        metadata={"role_id": role_id, "target_user": user_id},
    )
    await db.commit()

    return {"message": "Role removed from user"}

@router.post("/permissions/", response_model=PermissionRead)
async def create_permission(
    data: PermissionBase,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_roles("admin"))
):
    try:
        perm = await role_service.create_permission(db, data)
        await db.commit()

        await audit_service.log_action(
            db,
            user_id=admin.id,
            action_type=AuditAction.PERMISSION_CREATED,
            metadata={"permission": data.name},
        )
        await db.commit()

        return perm

    except ValueError as e:
        raise HTTPException(400, str(e))
    
@router.get("/permissions/", response_model=list[PermissionRead])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_roles("admin"))
):
    perms = await role_service.list_permissions(db)
    return perms


@router.post("/{role_id}/permissions/{perm_id}")
async def assign_permission(
    role_id: int,
    perm_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_roles("admin"))
):
    role = await role_service.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(404, "Role not found")

    
    perm = await role_service.get_permission_by_id(db, perm_id)
    
    if not perm:
        raise HTTPException(404, "Permission not found")

    await role_service.assign_permission_to_role(db, role, perm)
    await db.commit()

    await audit_service.log_action(
        db,
        user_id=admin.id,
        action_type=AuditAction.PERMISSION_ASSIGNED,
        metadata={"role_id": role_id, "perm_id": perm_id},
    )
    await db.commit()

    return {"message": "Permission assigned to role"}


@router.delete("/{role_id}/permissions/{perm_id}")
async def remove_permission(
    role_id: int,
    perm_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_roles("admin"))
):
    role = await role_service.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(404, "Role not found")

    perm = await db.get(role.__class__.permissions.property.mapper.class_, perm_id)
    if not perm:
        raise HTTPException(404, "Permission not found")

    await role_service.remove_permission_from_role(db, role, perm)
    await db.commit()

    await audit_service.log_action(
        db,
        user_id=admin.id,
        action_type=AuditAction.PERMISSION_REMOVED,
        metadata={"role_id": role_id, "perm_id": perm_id},
    )
    await db.commit()

    return {"message": "Permission removed from role"}