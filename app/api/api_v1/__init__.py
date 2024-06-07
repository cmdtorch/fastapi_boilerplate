from fastapi import APIRouter

from core.config import settings
from .auth import auth_route
from .mock_auth import mock_auth_route
from .user import user_route


router = APIRouter(prefix=settings.api.v1.prefix)

# Debug auth endpoints
if settings.debug:
    router.include_router(mock_auth_route, prefix=settings.api.v1.auth)

router.include_router(auth_route, prefix=settings.api.v1.auth)
router.include_router(user_route, prefix=settings.api.v1.user)

