from pydantic import BaseModel


class ExceptionResponseSchema(BaseModel):
    error_code: int
    message: str
