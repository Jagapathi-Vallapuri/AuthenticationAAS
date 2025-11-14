from pydantic import BaseModel


class AccessTokenData(BaseModel):
    user_id: int
    roles: list[str]
    token_version: int
    exp: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
