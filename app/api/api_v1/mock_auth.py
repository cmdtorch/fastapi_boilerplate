from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from core.exceptions.auth import UserDoesNotExistException, InvalidSocialTokenException
from core.schemas.auth import SocUserInfo, UserAuthData
from core.schemas.token import AccessRefreshToken
from services.user import user_service
from core.utils.token import TokenHelper

mock_auth_route = APIRouter(tags=['Auth'])
main_route = APIRouter()


@main_route.post("/token", summary="Login For Debug")
async def login_for_debug(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.password == '123':
        user = await user_service.get(email=form_data.username)
        access_token = TokenHelper.access_token(user.email)
        return {"access_token": access_token, "token_type": "bearer"}
    return None


@mock_auth_route.post('/mock_sing_up/', response_model=AccessRefreshToken, summary="Mock Social Sign Up User")
async def mock_sing_up(user_auth_data: UserAuthData = Depends()):
    # Mock soc information
    user_soc_data = SocUserInfo(
        email='test@test.com',
        full_name='Test Test',
    )
    if user_soc_data is None:
        raise InvalidSocialTokenException
    user = await user_service.create(user_soc_data, user_auth_data)
    return AccessRefreshToken(
        access_token=TokenHelper.access_token(user.email),
        refresh_token=TokenHelper.refresh_token(user.email)
    )


@mock_auth_route.post('/mock_sing_in/', response_model=AccessRefreshToken, summary="Mock Social Sign In User")
async def sing_in(user_auth: UserAuthData = Depends()):
    # Mock soc information
    user_soc_data = SocUserInfo(
        email='test@test.com',
        full_name='Test Test',
    )
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
