from enum import Enum
from typing import Optional, Literal

from typing_extensions import Self
from pydantic import BaseModel, model_validator

from core.config import settings


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
