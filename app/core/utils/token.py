from datetime import datetime, timedelta ,UTC

import jwt

from core.config import settings
from core.exceptions.token import TokenNotValidException, TokenExpiredException
from core.schemas.token import TokenPayloadEncode, TokenPayloadDecode


class TokenHelper:

    @staticmethod
    def access_token(email: str, exp: int = None) -> str:
        """
        Ecode access token for auth
        :param email: user email
        :param exp: token exp time, default value in config.py
        :return: Access token
        """
        return TokenHelper.encode(
            TokenPayloadEncode(
                sub=email,
                scope='access',
                exp=exp if exp else settings.auth.access_token_time,
            )
        )

    @staticmethod
    def refresh_token(email: str, exp: int = None) -> str:
        """
        Ecode refresh token for auth
        :param email: user email
        :param exp: token exp time, default value in config.py
        :return: Refresh token
        """
        return TokenHelper.encode(
            TokenPayloadEncode(
                sub=email,
                scope='refresh',
                exp=exp if exp else settings.auth.refresh_token_time,
            )
        )

    @staticmethod
    def encode(payload: TokenPayloadEncode) -> str:
        token = jwt.encode(
            payload={
                **payload.model_dump(exclude={'exp'}),
                "exp": datetime.now(UTC) + timedelta(seconds=payload.exp),
                'iat': datetime.now(UTC),
            },
            key=settings.auth.secret_key,
            algorithm=settings.auth.algorithm,
        )
        return token

    @staticmethod
    def decode(token: str) -> TokenPayloadDecode:
        try:
            return jwt.decode(
                token,
                settings.auth.secret_key,
                settings.auth.algorithm,
            )
        except jwt.exceptions.DecodeError:
            raise TokenNotValidException
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpiredException

    @staticmethod
    def decode_expired_token(token: str) -> TokenPayloadDecode:
        try:
            return jwt.decode(
                token,
                settings.auth.secret_key,
                settings.auth.algorithm,
                options={"verify_exp": False},
            )
        except jwt.exceptions.DecodeError:
            raise TokenNotValidException
