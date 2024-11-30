from app.core.db.transactional import Propagation, Transactional
from app.core.exceptions.auth import WrongTimezoneException
from app.core.models import User
from app.core.schemas.auth import UserAuthData
from app.core.utils import is_valid_timezone
from app.repository.user import UserRepository, user_repository

from .base import BaseService


class UserService(BaseService[User, UserRepository]):
    @Transactional(Propagation.REQUIRED)
    async def create_user(self, user_data: UserAuthData) -> User:
        user = User(**user_data.model_dump())
        return await self.repository.save(user)

    async def update_on_login(self, user: User, auth_data: UserAuthData) -> User:
        if not is_valid_timezone(auth_data.timezone):
            raise WrongTimezoneException

        return await user_repository.update(
            updates=auth_data.model_dump(exclude={"soc_type"}),
            instance=user,
        )


user_service = UserService(User, user_repository)
