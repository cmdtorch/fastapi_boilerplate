from fastapi import APIRouter, Depends

from app.core.exceptions.auth import (
    InvalidSocialTokenException,
    UserDoesNotExistException,
)
from app.core.schemas.auth import SocUserInfo, UserAuthData
from app.core.schemas.base import ExceptionResponseSchema
from app.core.schemas.token import AccessRefreshToken
from app.core.utils.token import TokenHelper
from app.services.social import SocAuth
from app.services.user import user_service

auth_route = APIRouter(tags=["Auth"])


@auth_route.post(
    "/sing_up/",
    response_model=AccessRefreshToken,
    responses={"400": {"model": ExceptionResponseSchema}},
    summary="Social Sign Up User",
)
async def sing_up(user_auth_data: UserAuthData = Depends()) -> AccessRefreshToken:
    user_soc_data = getattr(SocAuth, user_auth_data.soc_type.value)(
        user_auth_data.soc_token,
    )
    if user_soc_data is None:
        raise InvalidSocialTokenException
    user = await user_service.create_user(user_soc_data)
    return AccessRefreshToken(
        access_token=TokenHelper.access_token(user.email),
        refresh_token=TokenHelper.refresh_token(user.email),
    )


@auth_route.post(
    "/sing_in/",
    response_model=AccessRefreshToken,
    responses={"400": {"model": ExceptionResponseSchema}},
    summary="Social Sign In User",
)
async def sing_in(user_auth: UserAuthData = Depends()) -> AccessRefreshToken:
    user_soc_data: SocUserInfo = getattr(SocAuth, user_auth.soc_type.value)(
        user_auth.soc_token,
    )
    if user_soc_data is None:
        raise InvalidSocialTokenException

    # If user does not exist
    user = await user_service.get_by_filed(email=user_soc_data.email)
    if user is None:
        raise UserDoesNotExistException

    await user_service.update_on_login(user, user_auth)
    return AccessRefreshToken(
        access_token=TokenHelper.access_token(user.email),
        refresh_token=TokenHelper.refresh_token(user.email),
    )
