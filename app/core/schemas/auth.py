from enum import Enum

from pydantic import BaseModel


class SocType(Enum):
    google = "google"
    facebook = "facebook"
    apple = "apple"


class AuthExtraData(BaseModel):
    firebase_token: str
    timezone: str


class UserSocialData(BaseModel):
    email: str
    full_name: str | None = None


class SignInSocial(BaseModel):
    soc_token: str
    soc_type: SocType
    firebase_token: str
    timezone: str


class SignIn(BaseModel):
    email: str
    password: str
    firebase_token: str
    timezone: str
