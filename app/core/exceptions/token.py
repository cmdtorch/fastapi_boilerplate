from fastapi import status
from core.exceptions.base import CustomException


class TokenExpiredException(CustomException):
    code = status.HTTP_400_BAD_REQUEST
    error_code = status.HTTP_400_BAD_REQUEST
    message = "Token expired"


class TokenNotValidException(CustomException):
    code = status.HTTP_400_BAD_REQUEST
    error_code = status.HTTP_400_BAD_REQUEST
    message = "Token is not valid"


class WrongTokenScopeException(CustomException):
    code = status.HTTP_400_BAD_REQUEST
    error_code = status.HTTP_400_BAD_REQUEST
    message = "Token scope is not correct"
