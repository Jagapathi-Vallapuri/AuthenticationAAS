from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
    # App
    APP_NAME: str = "AuthenticationAAS"
    APP_ENV: str = "development"
    APP_BASE_URL: AnyHttpUrl = None

    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = 5432
    DB_NAME: Optional[str] = 'postgres'

    PRIVATE_KEY: Optional[str] = None
    PUBLIC_KEY: Optional[str] = None
    PRIVATE_KEY_PATH: Optional[Path] = None
    PUBLIC_KEY_PATH: Optional[Path] = None

    ACCESS_TOKEN_EXPIRES_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRES_DAYS: int = 30

    # Cookie names
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"

    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    SSL_CERTFILE: Optional[Path] = None
    SSL_KEYFILE: Optional[Path] = None

    @property
    def database_url(self) -> str:

        user = self.DB_USER or ""
        pwd = self.DB_PASSWORD or ""
        host = self.DB_HOST or "localhost"
        port = int(self.DB_PORT or 5432)
        name = self.DB_NAME or "postgres"

        return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{name}?sslmode=require"


settings = Settings()
