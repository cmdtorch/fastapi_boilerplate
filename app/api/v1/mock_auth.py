from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security.jwt import JWTHelper
from app.services.user import user_service

mock_auth_route = APIRouter(tags=["Auth"])
main_route = APIRouter()


@main_route.post("/token", summary="Login For Debug")
async def login_for_debug(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str] | None:
    if form_data.password == settings.auth.debug_password:
        user = await user_service.get(email=form_data.username)
        access_token = JWTHelper.access_token(user.email)
        return {"access_token": access_token, "token_type": "bearer"}
    return None
