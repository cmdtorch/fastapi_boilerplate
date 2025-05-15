from app.models import User
from app.repository.user import UserRepository, user_repository

from .base import BaseService


class UserService(BaseService[User, UserRepository]):
    pass


user_service = UserService(User, user_repository)
