import datetime
from typing import Optional, ClassVar, TypeVar

from pydantic import BaseModel, Field, ConfigDict, field_validator

from core.models import Base

UNCHANGED_VALUE = "UNCHANGED_VALUE"

ModelType = TypeVar('ModelType', bound=Base)


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


class PaddingSchema(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, le=250, default=15)


class SortSchema(BaseModel):
    sort_field: str = Field(default='id')
    desc: bool = Field(default=True)
    sort_case_ids: list[int] | None

    @field_validator('sort_case_ids', mode='before')
    @classmethod
    def convert_value(cls, sort_case_ids: str):
        if not sort_case_ids:
            return None
        sort_case_ids = sort_case_ids.split(",")  # type: ignore
        try:
            sort_case_ids = [int(v) for v in sort_case_ids]  # type: ignore
        except ValueError:
            return None
        return sort_case_ids


class SearchSchema(BaseModel):
    query: Optional[str] = None
    search_fields: Optional[list[str]] = Field(None, alias='fields')


class FilterItem(BaseModel):
    name: str
    value: str | int | bool

    @field_validator('value', mode='before')
    @classmethod
    def convert_value(cls, value: str):
        if value in ['true', 'false']:
            return True if value == 'true' else False  # type: ignore
        try:
            value = int(value)  # type: ignore
        except ValueError:
            pass
        return value


class FilterSchema(BaseModel):
    filters_or: list[FilterItem]
    filters_and: list[FilterItem]


