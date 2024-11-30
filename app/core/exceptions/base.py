from http import HTTPStatus
from typing import Any, ClassVar, Type

from app.core.schemas.base import ExceptionResponseSchema


class CustomException(Exception):  # noqa: N818
    code: ClassVar[int] = HTTPStatus.BAD_GATEWAY
    error_code: ClassVar[int] = HTTPStatus.BAD_GATEWAY
    message_code: ClassVar[str] = "bad_gateway"
    message: str = HTTPStatus.BAD_GATEWAY.description
    _schema: ClassVar[Type[ExceptionResponseSchema]] = ExceptionResponseSchema

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message

    @classmethod
    def example(cls) -> dict[str, Any]:  # type: ignore
        return {
            "summary": cls.__name__,
            "value": {
                "error_code": cls.error_code,
                "message_code": cls.message_code,
                "message": cls.message,
            },
        }

    @classmethod
    def content(
        cls,
    ) -> dict[str, Any]:  # type: ignore
        return {"application/json": {"examples": {cls.__name__: cls.example()}}}

    @classmethod
    def response(cls) -> dict[str, Any]:  # type: ignore
        return {
            "model": cls._schema,
            "description": cls.message,
            "content": cls.content(),
        }
