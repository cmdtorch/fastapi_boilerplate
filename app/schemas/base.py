import datetime
from typing import ClassVar, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.models import Base

UNCHANGED_VALUE = "UNCHANGED_VALUE"

ModelType = TypeVar("ModelType", bound=Base)


class UnchangedType:
    pass


UNCHANGED = UnchangedType()


class CrudSchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    extra_fields: ClassVar[set[str] | None] = None


class ExceptionResponseSchema(BaseModel):
    error_code: int
    message: str


class EventDate(BaseModel):
    create_date: datetime.datetime
    update_date: datetime.datetime


class PaginationGetter(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, le=250, default=15)
