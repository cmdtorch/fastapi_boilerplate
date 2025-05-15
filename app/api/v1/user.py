from fastapi import APIRouter

from app.core.exceptions.token import WrongTokenScopeException
from app.core.utils.token import TokenHelper
from app.schemas.token import AccessRefreshToken

user_route = APIRouter(tags=["User"])


@user_route.post(
    "/refresh_token/",
    response_model=AccessRefreshToken,
    summary="Refresh Token",
)
async def user_refresh_token(refresh_token: str) -> AccessRefreshToken:
    token_data = TokenHelper.decode(refresh_token)
    if token_data["scope"] != "refresh":
        raise WrongTokenScopeException
    return AccessRefreshToken(
        access_token=TokenHelper.access_token(token_data["email"]),
        refresh_token=refresh_token,
    )
