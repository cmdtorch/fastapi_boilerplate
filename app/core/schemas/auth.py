from enum import Enum
from typing import Optional

from pydantic import BaseModel


class SocType(Enum):
    google = 'google'
    facebook = 'facebook'
    apple = 'apple'


class SocUserInfo(BaseModel):
    email: str
    full_name: Optional[str] = None


class UserAuthData(BaseModel):
    soc_token: str
    firebase_token: str
    soc_type: SocType
    timezone: str

