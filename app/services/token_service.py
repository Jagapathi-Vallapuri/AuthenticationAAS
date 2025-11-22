from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional

import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


from app.models.RefreshToken import RefreshToken
from app.models.User import User
from app.models.Session import Session
from app.models.RevokedToken import RevokedToken

from app.services import session_service

from app.core.config import settings

ACCESS_TOKEN_EXPIRES_MINUTES = settings.ACCESS_TOKEN_EXPIRES_MINUTES
REFRESH_TOKEN_EXPIRES_DAYS = settings.REFRESH_TOKEN_EXPIRES_DAYS

def _load_private_key() -> str:
    """Load private key from settings (inline or file path)."""
    key = settings.PRIVATE_KEY
    if key:
        return key
    path = settings.PRIVATE_KEY_PATH
    if path and path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    raise RuntimeError("PRIVATE_KEY or PRIVATE_KEY_PATH must be set in settings")
    

def _load_public_key() -> str:
    key = settings.PUBLIC_KEY
    if key:
        return key
    path = settings.PUBLIC_KEY_PATH
    if path and path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    raise RuntimeError("PUBLIC_KEY or PUBLIC_KEY_PATH must be set in settings")

_PRIVATE_KEY = None
_PUBLIC_KEY = None

def _get_private_key():
    global _PRIVATE_KEY
    if _PRIVATE_KEY is None:
        _PRIVATE_KEY = _load_private_key()
    return _PRIVATE_KEY

def _get_public_key():
    global _PUBLIC_KEY
    if _PUBLIC_KEY is None:
        _PUBLIC_KEY = _load_public_key()
    return _PUBLIC_KEY

def _hash_secret(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()

def _now_utc()->datetime:
    return datetime.now(timezone.utc)

def verify_access_token(token: str) -> dict:
    
    pub = _get_public_key()
    payload = jwt.decode(token, pub, algorithms=["RS256"], options={"verify_aud": False})
    return payload

def create_access_token_for_user(user: User, extra_claims: dict | None =None):
    """
    """
    priv = _get_private_key()
    now = _now_utc()
    exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    jti = secrets.token_urlsafe(16)

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": jti,
    }

    if extra_claims:
        payload.update(extra_claims)
    
    token = jwt.encode(payload=payload, key=priv, algorithm="RS256")
    return token

async def create_refresh_token(
        db : AsyncSession,
        user: User,
        user_agent: Optional[str] = None,
        ip_addr: Optional[str] = None,
        expires_days: int = REFRESH_TOKEN_EXPIRES_DAYS
) -> Tuple[str, RefreshToken]:
    """
    """

    raw_secret = secrets.token_urlsafe(48)
    token_hash = _hash_secret(raw_secret)
    expires_at = _now_utc() + timedelta(days=expires_days)

    rt = RefreshToken(
        user_id = user.id,
        token_hash = token_hash,
        user_agent = user_agent,
        ip_address = ip_addr,
        created_at=_now_utc(),
        expires_at= expires_at,
        revoked=False
    )

    db.add(rt)
    await db.flush()

    token_str = f"{rt.id}-{user.id}-{raw_secret}"

    return token_str, rt

async def _get_refresh_token_by_id(db: AsyncSession, rt_id: int)-> Optional[RefreshToken]:
    res = await db.execute(select(RefreshToken).where(RefreshToken.id == rt_id))
    return res.scalar_one_or_none()

async def verify_refresh_token_and_get_row(db: AsyncSession, token_str: str) -> RefreshToken:
    try:
        rt_id, user_id, raw = token_str.split('-', 2)
        rt_id = int(rt_id)
        user_id = int(user_id)
    except Exception:
        raise ValueError("Invalid refresh token format")
    
    rt = await _get_refresh_token_by_id(db, rt_id)

    if not rt:
        try:
            await session_service.revoke_all_sessions(db, user_id)
        except Exception:
            pass
        raise ValueError("Invalid refresh token")
    
    if rt.expires_at < _now_utc(): #type:ignore
        raise ValueError("Refresh token expired")
    
    if rt.revoked: #type:ignore
        try:
            await session_service.revoke_all_sessions(db, rt.user_id) #type: ignore
        except Exception:
            pass
        raise ValueError("Refresh token revoked")
    
    expected_hash = rt.token_hash #type:ignore

    if _hash_secret(raw) != expected_hash:
        try:
            await session_service.revoke_all_sessions(db, rt.user_id) #type: ignore
        except Exception:
            pass
        raise ValueError("Invalid refresh token")
    
    return rt #type: ignore

async def rotate_refresh_token(
        db: AsyncSession,
        presented_token: str,
        user_agent: Optional[str] = None,
        ip_addr: Optional[str] = None
) -> Tuple[str, RefreshToken]:
    """
    """

    rt = await verify_refresh_token_and_get_row(db, presented_token)

    user = await db.get(User, rt.user_id)

    if not user:
        raise ValueError("Invalid refresh token user")
    
    new_token_str, new_rt = await create_refresh_token(
        db, user, user_agent, ip_addr
    )

    rt.revoked = True #type: ignore

    res = await db.execute(select(Session).where(Session.refresh_token_id == rt.id))
    session_obj = res.scalar_one_or_none()

    if session_obj:
        session_obj.refresh_token_id = new_rt.id
        session_obj.last_used_at = _now_utc() #type: ignore
    
    await db.flush()

    return new_token_str, new_rt

async def revoke_refresh_token(db: AsyncSession, token_str: str) -> bool:
    """
    """
    try:
        rt_id_str, _, _ = token_str.split("-", 2)
        rt_id = int(rt_id_str)
    except Exception:
        return False
    
    rt = await _get_refresh_token_by_id(db, rt_id)

    if not rt:
        return False
    
    rt.revoked = True # type: ignore

    if rt and rt.session:
        rt.session.revoked = True
    
    await db.flush()

    return True


async def revoke_all_refresh_tokens_for_user(db: AsyncSession, user_id: int):
    
    await db.execute(
        update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True)
    )
    await session_service.revoke_all_sessions(db, user_id)
    await db.flush()
    return True

async def revoke_access_token_jti(db: AsyncSession, jti: str):

    item = RevokedToken(jti=jti)
    db.add(item)
    await db.flush()

async def is_access_token_revoked(db: AsyncSession, jti: str) -> bool:
    result = await db.execute(select(RevokedToken).where(RevokedToken.jti == jti))
    return result.scalar_one_or_none() is not None