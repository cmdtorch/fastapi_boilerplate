from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions.auth import CredentialsException, IncorrectCredentialsException
from app.core.models.user import User
from app.core.utils.token import TokenHelper
from app.services.user import user_service


class AuthService:
    hasher = CryptContext(schemes=["bcrypt"])
    secret = settings.auth.secret_key
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @classmethod
    async def get_current_active_user(cls, token: str = Depends(oauth2_scheme)) -> User:
        token_data = TokenHelper.decode(token)
        user = await cls.get_user(token_data["sub"])
        if user is None:
            raise CredentialsException

        if user.is_deleted:
            raise HTTPException(status_code=400, detail="User is Deleted")

        return user

    @classmethod
    async def get_user(cls, email: str) -> User:
        user: User = await user_service.get_by_filed(email=email)

        if user is None:
            raise CredentialsException
        return user

    @classmethod
    async def authenticate_user(cls, email: str) -> User:
        user = await cls.get_user(email)
        if not user:
            raise IncorrectCredentialsException

        return user

    @classmethod
    def verify_password(cls, password: str, encode_password: str) -> bool:
        return cls.hasher.verify(password, encode_password)
