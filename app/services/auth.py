import os
import jwt
import datetime
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper
from core.exceptions.auth import CredentialsException, IncorrectCredentialsException
from core.models.user import User
from services.user import user_service
from core.utils.token import TokenHelper


class AuthService:
    hasher = CryptContext(schemes=['bcrypt'])
    secret = settings.auth.secret_key
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @classmethod
    async def get_current_active_user(cls, token: str = Depends(oauth2_scheme)):
        email, _ = TokenHelper.decode(token)
        user = await cls.get_user(email)
        if user is None:
            raise CredentialsException

        if user.is_deleted:
            raise HTTPException(status_code=400, detail="User is Deleted")

        return user

    @classmethod
    async def get_user(cls, email: str):
        user: User = await user_service.get(email)

        if user is None:
            raise CredentialsException
        return user

    @classmethod
    async def authenticate_user(cls, email: str):
        user = await cls.get_user(email)
        if not user:
            raise IncorrectCredentialsException

        return user

    @classmethod
    def verify_password(cls, password, encode_password):
        return cls.hasher.verify(password, encode_password)
