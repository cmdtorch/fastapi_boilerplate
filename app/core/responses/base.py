from typing import Any

from app.core.exceptions.base import CustomException


class ExceptionResponses:
    def __new__(cls, *exceptions: type[CustomException]) -> dict[str, Any]:  # type: ignore
        responses: dict[int, dict[str, Any]] = {}
        for exception in exceptions:
            if exception.code in responses:
                responses[exception.code]["content"]["application/json"]["examples"][
                    exception.__name__
                ] = exception.example()
            else:
                responses[exception.code] = {"content": exception.content()}
        return responses  # type: ignore
