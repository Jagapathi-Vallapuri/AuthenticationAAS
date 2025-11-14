from app.schemas.user import UserCreate
from app.schemas.password import PasswordResetConfirm

from app.models.User import User
from app.models.EmailVerificationToken import EmailVerificationToken
from app.models.PasswordRestToken import PasswordResetToken

from passlib.context import CryptContext
from pydantic import EmailStr
import hashlib
import secrets
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

async def register_user(db: AsyncSession, user: UserCreate) -> User:
    res = await db.execute(select(User).where(User.email == user.email))
    existing = res.scalar_one_or_none()
    if existing:
        raise ValueError("User already exists")
    
    hashed_pw = hash_password(user.password)
    new_user = User(
        email = user.email,
        password_hash = hashed_pw,
        is_active = True,
        is_verified = False
    )

    db.add(new_user)
    await db.flush()

    await create_email_verification_token(db, new_user)

    await db.commit()
    await db.refresh(new_user)
    
    return new_user

async def authenticate_user(db: AsyncSession, email:EmailStr, password:str) -> User:
    
    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()

    if not user:
        raise ValueError("Invalid email")
    
    if user.is_active is False:
        raise ValueError("User account is deactivated")
    
    if verify_password(password, user.password_hash) is False: #type: ignore
        raise ValueError("Invalid credentials")
    
    return user


async def verify_email_token(db:AsyncSession, raw_token:str) -> bool:
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    res = await db.execute(
        select(EmailVerificationToken)
        .where(EmailVerificationToken.token_hash == token_hash)
    )

    token = res.scalar_one_or_none()
    if not token:
        raise ValueError("Invalid token")
    
    if token.used is True:
        raise ValueError("Token already used")
    
    if datetime.utcnow() > token.expires_at: #type: ignore
        raise ValueError("Token expired")
    
    token.used = True  # type: ignore

    user = await db.get(User, token.user_id)
    user.is_verified = True #type: ignore

    await db.commit()

    return True


async def reset_password(db: AsyncSession, new_password: PasswordResetConfirm):
    token_hash = hashlib.sha256(new_password.token.encode()).hexdigest()

    res = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )

    token = res.scalar_one_or_none()

    if not token:
        raise ValueError("Invalid password reset token")
    
    if token.used is False:
        raise ValueError("Token already used")
    
    if datetime.utcnow() > token.expires_at: #type: ignore
        raise ValueError("Token expired")

    user = await db.get(User, token.user_id)
    user.password_hash = hash_password(new_password.new_password) #type: ignore

    token.used = True #type: ignore

    await db.commit()
    return True
    pass


async def create_email_verification_token(db: AsyncSession, user: User):
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    token = EmailVerificationToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=24),
        used=False,
    )

    db.add(token)
    await db.flush()

    return raw_token