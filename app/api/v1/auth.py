from fastapi import APIRouter

from app.core.exceptions.auth import (
    UserDoesNotExistException,
)
from app.core.exceptions.entity import RecordNotFound
from app.core.security.jwt import JWTHelper
from app.schemas.auth import SignIn
from app.schemas.base import ExceptionResponseSchema
from app.schemas.token import AccessRefreshToken
from app.services.user import user_service

auth_route = APIRouter(tags=["Auth"])


@auth_route.post(
    "/sign_in/",
    response_model=AccessRefreshToken,
    responses={"400": {"model": ExceptionResponseSchema}},
    summary="Social Sign In User",
)
async def sign_in(user_auth_data: SignIn) -> AccessRefreshToken:
    try:
        user = await user_service.get(email=user_auth_data.email)
    except RecordNotFound as e:
        # If user does not exist
        raise UserDoesNotExistException from e

    return AccessRefreshToken(
        access_token=JWTHelper.access_token(user.email),
        refresh_token=JWTHelper.refresh_token(user.email),
    )
