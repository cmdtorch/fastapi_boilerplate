from pydantic import BaseModel


class TokenPayloadEncode(BaseModel):
    sub: str
    scope: str
    exp: int


class TokenPayloadDecode(BaseModel):
    sub: str
    scope: str
    exp: int
    iat: int


class AccessRefreshToken(BaseModel):
    access_token: str
    refresh_token: str
