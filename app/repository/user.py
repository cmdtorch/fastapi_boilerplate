from app.models import User
from app.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self) -> None:
        super().__init__(User)


user_repository = UserRepository()
