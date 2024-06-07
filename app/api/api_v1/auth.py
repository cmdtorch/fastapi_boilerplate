from fastapi import APIRouter, Depends

from core.exceptions.auth import UserDoesNotExistException, InvalidSocialTokenException
from core.schemas.auth import SocUserInfo, UserAuthData
from core.schemas.base import ExceptionResponseSchema
from core.schemas.token import AccessRefreshToken
from core.utils.token import TokenHelper
from services.social import SocAuth
from services.user import user_service

auth_route = APIRouter(tags=['Auth'])


@auth_route.post(
    '/sing_up/',
    response_model=AccessRefreshToken,
    responses={"400": {"model": ExceptionResponseSchema}},
    summary="Social Sign Up User"
)
async def sing_up(user_auth_data: UserAuthData = Depends()):
    user_soc_data = getattr(SocAuth, user_auth_data.soc_type.value)(user_auth_data.soc_token)
    if user_soc_data is None:
        raise InvalidSocialTokenException
    user = await user_service.create(user_soc_data, user_auth_data)
    return AccessRefreshToken(
        access_token=TokenHelper.access_token(user.email),
        refresh_token=TokenHelper.refresh_token(user.email)
    )


@auth_route.post(
    '/sing_in/',
    response_model=AccessRefreshToken,
    responses={"400": {"model": ExceptionResponseSchema}},
    summary="Social Sign In User"
)
async def sing_in(user_auth: UserAuthData = Depends()):
    user_soc_data: SocUserInfo = getattr(SocAuth, user_auth.soc_type.value)(user_auth.soc_token)
    if user_soc_data is None:
        raise InvalidSocialTokenException

    # If user does not exist
    user = await user_service.get(user_soc_data.email)
    if user is None:
        raise UserDoesNotExistException

    await user_service.update_on_login(user, user_auth)
    return AccessRefreshToken(
        access_token=TokenHelper.access_token(user.email),
        refresh_token=TokenHelper.refresh_token(user.email)
    )
