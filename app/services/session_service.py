from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select

from app.models.User import User
from app.models.RefreshToken import RefreshToken
from app.models.Session import Session

async def create_session(
        db: AsyncSession,
        user: User,
        refresh_token: RefreshToken,
        device_token: str | None = None
) -> Session:
    session = Session(
        user_id= user.id,
        refresh_token_id = refresh_token.id,
        device_info = device_token,
        last_used_at = datetime.utcnow(),
        revoked = False,
    )

    db.add(session)
    await db.flush()

    return session

async def touch_session(db: AsyncSession, session_id: int):
    await db.execute(
        update(Session)
        .where(Session.id == session_id)
        .values(last_used_at=datetime.utcnow())
    )
    await db.flush()


async def revoke_session(db: AsyncSession, session_id: int) -> bool:
    res = await db.execute(
        select(Session). where(Session.id == session_id)
    )

    session = res.scalar_one_or_none()

    if not session:
        return False
    
    session.revoked = True #type: ignore

    if session.refresh_token:
        session.refresh_token.revoked = True
    
    await db.commit()

    return True

async def revoke_all_sessions(db: AsyncSession, user_id: int):
    res = await db.execute(
        select(Session).where(Session.user_id == user_id)
    )
    sessions = res.scalars().all()

    for s in sessions:
        s.revoked = True # type: ignore
        if s.refresh_token:
            s.refresh_token.revoked = True
    
    await db.commit()

    return True

async def get_user_sessions(db: AsyncSession, user_id: int) -> List[Session]:
    result = await db.execute(
        select(Session)
        .where(Session.user_id == user_id)
        .order_by(Session.last_used_at.desc())
    )
    return list(result.scalars().all())


async def get_session_by_refresh_token(db: AsyncSession, refresh_token_id: int) -> Session | None:
    result = await db.execute(
        select(Session).where(Session.refresh_token_id == refresh_token_id)
    )
    return result.scalar_one_or_none()