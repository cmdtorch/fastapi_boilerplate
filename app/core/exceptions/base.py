from http import HTTPStatus

from core.schemas.base import ExceptionResponseSchema


class CustomException(Exception):
    code = HTTPStatus.BAD_GATEWAY
    error_code = HTTPStatus.BAD_GATEWAY
    message = HTTPStatus.BAD_GATEWAY.description
    _schema = ExceptionResponseSchema

    def __init__(self, message=None):
        if message:
            self.message = message

    @classmethod
    def example(cls):
        return {
            "summary": cls.__name__,
            "value": {
                "error_code": cls.error_code,
                "message": cls.message,
            }
        }

    @classmethod
    def content(cls):
        return {
            "application/json": {
                "examples": {
                    cls.__name__: cls.example()
                }
            }
        }

    @classmethod
    def response(cls):
        return {
            "model": cls._schema,
            "description": cls.message,
            "content": cls.content()
        }
