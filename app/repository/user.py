from core.models.user import User
from repository.base import BaseRepository


class UserRepository(BaseRepository):

    def __init__(self):
        super().__init__(User)


user_repository = UserRepository()
