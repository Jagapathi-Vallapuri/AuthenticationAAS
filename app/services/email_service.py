from __future__ import annotations

import os 
import aiosmtplib
from email.message import EmailMessage
from typing import Optional

from app.models.User import User

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM")

APP_BASE_URL = os.getenv("APP_BASE_URL")


async def _send_email_async(
    to_email: str,
    subject: str,
    html_content: str,
) -> bool:

    if not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD and SMTP_FROM):
        raise RuntimeError("SMTP configuration not set properly")

    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content("This email requires HTML support.")
    msg.add_alternative(html_content, subtype="html")

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
        )
        return True

    except Exception:
        return False


async def send_verification_email(user: User, raw_token: str) -> bool:
    verify_url = f"{APP_BASE_URL}/verify-email.html?token={raw_token}"

    html = f"""
    <html>
    <body>
        <p>Hello {user.email},</p>
        <p>To verify your account, click the link below:</p>
        <p><a href="{verify_url}">Verify Email</a></p>
        <br/>
        <p>If you did not request this, you can safely ignore this email.</p>
    </body>
    </html>
    """
    return await _send_email_async(
        to_email=user.email, #type: ignore
        subject="Verify your email",
        html_content=html,
    )

async def send_password_reset_email(user: User, raw_token: str) -> bool:
    """
    Sends a password reset link to the user.
    """

    reset_url = f"{APP_BASE_URL}/reset-password?token={raw_token}"

    html = f"""
    <html>
    <body>
        <p>Hello {user.email},</p>
        <p>You requested to reset your password. Click the link below:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <br/>
        <p>If this was not you, we strongly recommend changing your password.</p>
    </body>
    </html>
    """

    return await _send_email_async(
        to_email=user.email, #type: ignore
        subject="Password Reset Request",
        html_content=html,
    )

async def send_generic_email(
    to_email: str,
    subject: str,
    message_html: str,
) -> bool:
    return await _send_email_async(
        to_email=to_email,
        subject=subject,
        html_content=message_html,
    )