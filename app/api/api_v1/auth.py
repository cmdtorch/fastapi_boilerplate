from fastapi import APIRouter

from app.core.exceptions.auth import (
    UserDoesNotExistException,
)
from app.core.exceptions.entity import RecordNotFound
from app.core.schemas.auth import SignIn
from app.core.schemas.base import ExceptionResponseSchema
from app.core.schemas.token import AccessRefreshToken
from app.core.utils.token import TokenHelper
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
        user = await user_service.get_by_filed(email=user_auth_data.email)
    except RecordNotFound as e:
        # If user does not exist
        raise UserDoesNotExistException from e

    await user_service.update_on_login(user, user_auth_data)
    return AccessRefreshToken(
        access_token=TokenHelper.access_token(user.email),
        refresh_token=TokenHelper.refresh_token(user.email),
    )
