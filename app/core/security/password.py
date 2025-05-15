from passlib.context import CryptContext

from app.core.config import settings


class HashHelper:
    hasher = CryptContext(schemes=["bcrypt"])
    secret = settings.auth.secret_key

    @classmethod
    def verify_password(cls, password: str, encode_password: str) -> bool:
        return cls.hasher.verify(password, encode_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.hasher.hash(password)
