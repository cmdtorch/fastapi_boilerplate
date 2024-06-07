from core.exceptions.auth import WrongTimezoneException, UserDoesNotExistException
from core.models import User
from core.schemas.auth import UserAuthData
from repository.user import user_repository
from core.utils import is_valid_timezone


class UserService:

    async def get(self, email: str) -> User:
        user = await user_repository.get(email=email)
        if user is None:
            raise UserDoesNotExistException
        return user

    async def update_on_login(self, user: User, auth_data: UserAuthData):
        if not is_valid_timezone(auth_data.timezone):
            raise WrongTimezoneException

        user = await user_repository.update(updates=auth_data.model_dump(exclude={'soc_type'}), instance=user)
        return user


user_service = UserService()
