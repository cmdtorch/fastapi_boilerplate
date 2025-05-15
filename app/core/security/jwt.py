from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings
from app.core.exceptions.token import TokenExpiredException, TokenNotValidException
from app.schemas.token import TokenPayloadEncode


class JWTHelper:
    @staticmethod
    def access_token(email: str, exp: int | None = None) -> str:
        """
        Ecode access token for auth
        :param email: user email
        :param exp: token exp time, default value in env
        :return: Access token
        """
        return JWTHelper.encode(
            TokenPayloadEncode(
                sub=email,
                scope="access",
                exp=exp if exp else settings.auth.access_token_time,
            ),
        )

    @staticmethod
    def refresh_token(email: str, exp: int | None = None) -> str:
        """
        Ecode refresh token for auth
        :param email: user email
        :param exp: token exp time, default value in env
        :return: Refresh token
        """
        return JWTHelper.encode(
            TokenPayloadEncode(
                sub=email,
                scope="refresh",
                exp=exp if exp else settings.auth.refresh_token_time,
            ),
        )

    @staticmethod
    def encode(payload: TokenPayloadEncode) -> str:
        return jwt.encode(
            payload={
                **payload.model_dump(exclude={"exp"}),
                "exp": datetime.now(UTC) + timedelta(seconds=payload.exp),
                "iat": datetime.now(UTC),
            },
            key=settings.auth.secret_key,
            algorithm=settings.auth.algorithm,
        )

    @staticmethod
    def decode(token: str, verify: bool = True) -> dict[str, str]:
        try:
            return jwt.decode(
                token,
                settings.auth.secret_key,
                settings.auth.algorithm,
                options={"verify_signature": verify, "verify_exp": verify},
            )
        except jwt.exceptions.DecodeError:
            raise TokenNotValidException from None
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpiredException from None
