from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user, require_roles
from app.schemas.session import SessionRead
from app.models.AuditAction import AuditAction
from app.services import session_service, audit_service

router = APIRouter(tags=['Sessions'])

@router.get(path='/', response_model=list[SessionRead])
async def list_my_sessions(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    sessions = await session_service.get_user_sessions(db, current_user.id)
    return sessions

@router.post('/{session_id}/revoke')
async def revoke_my_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    curr_user = Depends(get_current_user)
):
    sessions = await session_service.get_user_sessions(db, curr_user.id)
    session_ids = {s.id for s in sessions}

    if session_id not in session_ids:
        raise HTTPException(403, "You cannot revoke another user's session")
    
    ok = await session_service.revoke_session(db, session_id)
    if not ok:
        raise HTTPException(404, 'Session not found')
    
    await db.commit()

    await audit_service.log_action(
        db,
        curr_user.id,
        AuditAction.SESSION_REVOKED,
        {'session_id': session_id}
    )

    await db.commit()

    return {'message': 'Session revoked'}

@router.post("/revoke-all")
async def revoke_all_my_sessions(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    await session_service.revoke_all_sessions(db, current_user.id)
    await db.commit()

    await audit_service.log_action(
        db,
        user_id=current_user.id,
        action_type=AuditAction.ALL_SESSIONS_REVOKED,
        metadata={"user_id": current_user.id},
    )
    await db.commit()

    return {"message": "All sessions revoked"}

@router.get('/all', response_model=list[SessionRead])
async def list_all_sessions(
    db: AsyncSession = Depends(get_db),
    _admin = Depends(require_roles('admin'))
):
    from app.models.Session import Session

    res = await db.execute(Session.__table__.select())
    rows = res.all()

    sessions = [Session(**dict(row)) for row in rows]
    return sessions

@router.post('/{session_id}/force-revoke')
async def force_revoke_session(session_id:int, db: AsyncSession, admin = Depends(require_roles('admin'))):
    ok = await session_service.revoke_session(db, session_id)
    if not ok:
        raise HTTPException(404, 'Session not found')
    await db.commit()

    await audit_service.log_action(
        db,
        admin.id,
        AuditAction.SESSION_FORCE_REVOKED,
        metadata={'session_id': session_id}
    )

    await db.commit()
    return {'message': 'Session revoked by admin'}