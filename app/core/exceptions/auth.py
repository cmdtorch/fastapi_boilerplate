from http import HTTPStatus
from fastapi import HTTPException, status

from .base import CustomException


class UserDoesNotExistException(CustomException):
    code = status.HTTP_400_BAD_REQUEST
    error_code = status.HTTP_400_BAD_REQUEST
    message = 'User with this email not found'


class InvalidSocialTokenException(CustomException):
    code = status.HTTP_400_BAD_REQUEST
    error_code = status.HTTP_400_BAD_REQUEST
    message = "Social token is invalid"


class CredentialsException(CustomException):
    code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED
    message = "Could not validate credentials"


class ConflictEmailException(CustomException):
    code = status.HTTP_409_CONFLICT
    error_code = status.HTTP_409_CONFLICT
    message = "User with this email already exist"


class ConflictUsernameException(CustomException):
    code = status.HTTP_409_CONFLICT
    error_code = status.HTTP_409_CONFLICT
    message = "User with this username already exist"


class IncorrectCredentialsException(CustomException):
    code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED
    message = "Incorrect username or password"


class UnprocessableEntityException(CustomException):
    code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    message = "Unprocessable entity"


class WrongCodeException(CustomException):
    code = status.HTTP_400_BAD_REQUEST
    error_code = status.HTTP_400_BAD_REQUEST
    message = "Wrong code"


class WrongTimezoneException(CustomException):
    code = status.HTTP_400_BAD_REQUEST
    error_code = status.HTTP_400_BAD_REQUEST
    message = "Wrong timezone"
