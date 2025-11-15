from __future__ import annotations


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import user_service, audit_service
from app.db.database import get_db
from app.core.security import get_current_active_user, get_current_user, require_roles
from app.schemas.user import UserRead, UserUpdate
from app.models.AuditAction import AuditAction

router = APIRouter(tags=['Users'])

@router.get('/me', response_model=UserRead)
async def get_me(
        curr_user = Depends(get_current_active_user)
):
    return curr_user

@router.patch('/me', response_model=UserRead)
async def update_me(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    curr_user = Depends(get_current_active_user)
):
    updated_user =  await user_service.update_user(db, curr_user, data)
    await db.commit()

    await audit_service.log_action(
        db,
        user_id=curr_user.id,
        action_type=AuditAction.USER_UPDATED,
        metadata= {'fields': list(data.dict(exclude_none=True).keys())}
    )

    await db.commit()

    return updated_user

