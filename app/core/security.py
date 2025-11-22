from __future__ import annotations

import os

from typing import Optional, List, Callable, Sequence
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, Security, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.User import User
from app.core.config import settings
from app.services import token_service, role_service
from app.db.database import get_db
from app.services.role_service import get_user_permissions, get_user_roles

bearer_scheme = HTTPBearer(auto_error = False)

ACCESS_TOKEN_COOKIE_NAME = settings.ACCESS_TOKEN_COOKIE_NAME


async def get_token_from_header_or_cookie(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> Optional[str]:
    if credentials and credentials.scheme.lower() == 'bearer':
        return credentials.credentials
    
    token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)

    if token:
        return token
    
    return None

def _unauth_exc(detail: str ="could not validate credentials"):
    return HTTPException( 
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers= {'WWW-Authenticate': 'Bearer'},
    )

def _forbidden_exc(detail: str = "Forbidden"):
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = detail)

def verify_access_token(token: str) -> dict:
    try:
        payload = token_service.verify_access_token(token)
    except Exception as exc:
        raise _unauth_exc()
    return payload

async def get_current_user(
        token: Optional[str] = Depends(get_token_from_header_or_cookie),
        db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise _unauth_exc("Authorization token not provided.")
    
    payload = verify_access_token(token)

    sub = payload.get('sub')
    jti = payload.get('jti')

    if not sub or not jti:
        raise _unauth_exc()
    
    try:
        revoked = await token_service.is_access_token_revoked(db, jti)
    except Exception:
        raise _unauth_exc()
    
    if revoked:
        raise _unauth_exc("Token revoked")
    
    try:
        user_id = int(sub)
    except Exception:
        raise _unauth_exc()
    
    user = await db.get(User, user_id)
    if not user:
        raise _unauth_exc("User not found")
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
  
    if not current_user.is_active: #type: ignore
        raise _forbidden_exc("User account is deactivated")
    
    if not current_user.is_verified: #type: ignore
        raise _forbidden_exc("Email address is not verified")
    
    return current_user

def require_roles(*required_roles: str) -> Callable[..., None]:

    async def _dependency(
            current_user: User = Depends(get_current_user),
            db : AsyncSession = Depends(get_db),
    ):
        roles = await get_user_roles(db, current_user.id) #type: ignore
        role_names = {r.name for r in roles}

        for r in required_roles:
            if r in role_names:
                return current_user
        
        raise _forbidden_exc("Insufficient role")
    
    return _dependency