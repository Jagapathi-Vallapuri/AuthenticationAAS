from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import LoginResponse, LoginRequest
from app.schemas.token import RefreshTokenRequest, RefreshTokenResponse
from app.schemas.password import PasswordResetRequest, PasswordResetConfirm
from app.schemas.email import EmailVerificationRequest, EmailVerificationConfirm
from app.models.AuditAction import AuditAction
from app.db.database import get_db
from app.services import auth_service, email_service, audit_service, token_service, session_service, user_service
from app.core.security import get_current_user

router = APIRouter(tags = ['Auth'])

@router.post('/register', response_model=UserRead)
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.register_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    raw_token = await auth_service.create_email_verification_token(db, user)

    await email_service.send_verification_email(user, raw_token)
    await audit_service.log_action(
        db,
        user_id=user.id,
        action_type=AuditAction.USER_REGISTERED,
        metadata={ 'email': user.email}
    )

    await db.commit()

    return user

@router.post('/login', response_model=LoginResponse)
async def login(req: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    client_ip = req.client.host
    user_agent = req.headers.get('user-agent')

    try:
        user = await auth_service.authenticate_user(db, data.email, data.password)
    except ValueError:
        await audit_service.log_action(
            db,
            user_id = None,
            action_type=AuditAction.LOGIN_FAILED,
            metadata={
                'email': data.email,  'ip': client_ip
            }
        )

        await db.commit()
        raise HTTPException(status_code=400, detail='Invalid email or password')
    
    access_token = token_service.create_access_token_for_user(user)
    refresh_token_str, refresh_obj  = await token_service.create_refresh_token(db, user, user_agent=user_agent, ip_addr=client_ip)

    session = await session_service.create_session(
        db, user, refresh_obj, device_token=user_agent
    )

    await audit_service.log_action(
        db,
        user_id=user.id,
        action_type=AuditAction.LOGIN_SUCCESS,
        metadata={"session_id": session.id, "ip": client_ip}
    )

    await db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token_str
    )

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    req: Request,
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    client_ip = req.client.host
    user_agent = req.headers.get("user-agent")

    try:
        new_refresh_str, new_refresh_obj = await token_service.rotate_refresh_token(
            db, data.refresh_token, user_agent=user_agent, ip_addr=client_ip
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    
    user = await db.get(new_refresh_obj.__class__.user.property.mapper.class_, new_refresh_obj.user_id)
    access_token = token_service.create_access_token_for_user(user)


    await audit_service.log_action(
        db, user_id=user.id, action_type=AuditAction.TOKEN_REFRESHED,
        metadata={"new_refresh_id": new_refresh_obj.id}
    )

    await db.commit()
    return RefreshTokenResponse(access_token=access_token, refresh_token=new_refresh_str)

@router.post('/logout')
async def logout(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    await token_service.revoke_refresh_token(db, data.refresh_token)

    await audit_service.log_action(
        db,
        user_id=user.id,
        action_type=AuditAction.LOGOUT
    )

    await db.commit()

    return {'message' : 'Logged out'}

@router.post('/logout-all')
async def logout_all(
    db: AsyncSession = Depends(get_db),
    curr_user = Depends(get_current_user)
):
    await token_service.revoke_all_refresh_tokens_for_user(db, curr_user.id)

    await audit_service.log_action(
        db,
        user_id=curr_user.id,
        action_type=AuditAction.LOGOUT,
    )

    await db.commit()

    return {"message": "Logged out from all devices"}

@router.post("/verify-email/request")
async def request_verification(
    req: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await user_service.get_user_by_email(db, req.email)
    if not user:
        return {"message": "If account exists, email will be sent"}

    raw = await auth_service.create_email_verification_token(db, user)
    await email_service.send_verification_email(user, raw)
    await db.commit()
    return {"message": "Verification email sent"}

@router.post("/verify-email/confirm")
async def confirm_verification(
    data: EmailVerificationConfirm,
    db: AsyncSession = Depends(get_db)
):
    try:
        await auth_service.verify_email_token(db, data.token)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Email verified successfully"}


@router.post('/password-reset/request')
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await user_service.get_user_by_email(db, data.email)
    raw = await auth_service.create_email_verification_token(db, user)

    if raw:
        await email_service.send_password_reset_email(user, raw)
        await db.commit()

    return { 'message': 'If an account exists, a reset email has been sent'}

@router.post('/password-reset/comfirm')
async def confirm_reset(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    try:
        await auth_service.reset_password(db, data)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {'message': 'Password reset successful'}