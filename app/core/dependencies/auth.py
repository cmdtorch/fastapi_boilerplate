from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions.auth import CredentialsException
from app.core.security.jwt import JWTHelper
from app.models import User
from app.services.user import user_service


class AuthService:
    hasher = CryptContext(schemes=["bcrypt"])
    secret = settings.auth.secret_key
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @classmethod
    async def get_current_active_user(cls, token: str = Depends(oauth2_scheme)) -> User:
        token_data = JWTHelper.decode(token)
        user = await cls._get_user(token_data["sub"])
        if user is None:
            raise CredentialsException

        if user.is_deleted:
            raise HTTPException(status_code=400, detail="User is Deleted")

        return user

    @classmethod
    async def _get_user(cls, email: str) -> User:
        user: User = await user_service.get(email=email)

        if user is None:
            raise CredentialsException
        return user
