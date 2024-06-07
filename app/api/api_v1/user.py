from fastapi import APIRouter

from core.exceptions.token import WrongTokenScopeException
from core.schemas.token import AccessRefreshToken
from core.utils.token import TokenHelper

user_route = APIRouter(tags=['User'])


@user_route.post('/refresh_token/', response_model=AccessRefreshToken, summary="Refresh Token")
async def user_refresh_token(refresh_token: str):
    token_data = TokenHelper.decode(refresh_token)
    if token_data.scope != 'refresh':
        raise WrongTokenScopeException
    return AccessRefreshToken(
        access_token=TokenHelper.access_token(token_data.email),
        refresh_token=refresh_token
    )
