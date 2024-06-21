from typing import Type

from core.exceptions.base import CustomException


class ExceptionResponses:

    def __new__(cls, *exceptions: Type[CustomException]):
        responses = {}
        for exception in exceptions:
            if responses.get(exception.code):
                responses[exception.code]['content']['application/json']['examples'][
                    exception.__name__] = exception.example()
            else:
                responses[exception.code] = {"content": exception.content()}
        return responses
