import contextlib
import datetime
from typing import ClassVar, ForwardRef, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.models import Base

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


class PaddingSchema(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, le=250, default=15)


class SortSchema(BaseModel):
    sort_field: str = Field(default="id")
    desc: bool = Field(default=True)
    sort_case_ids: list[int] | None

    @field_validator("sort_case_ids", mode="before")
    @classmethod
    def convert_value(cls, sort_case_ids: str) -> None | list[int]:
        if not sort_case_ids:
            return None
        sort_case_ids_list = sort_case_ids.split(",")
        try:
            return [int(v) for v in sort_case_ids_list]
        except ValueError:
            return None


SearchItemRef = ForwardRef("SearchItem")


class SearchItem(BaseModel):
    name: str
    value: str | SearchItemRef  # type: ignore


class SearchSchema(BaseModel):
    search: list[SearchItem]


FilterItemRef = ForwardRef("FilterItem")


class FilterItem(BaseModel):
    name: str
    value: str | int | bool | datetime.datetime | FilterItemRef  # type: ignore

    @field_validator("value", mode="before")
    @classmethod
    def convert_value(
        cls,
        value: str,
    ) -> dict[str, str] | bool | int | str | datetime.datetime:
        # Nest filter
        if isinstance(value, dict):
            return value
        # Boolean value
        if value in ["true", "false"]:
            return value == "true"
        # DateTime
        with contextlib.suppress(ValueError):
            return datetime.datetime.strptime(value, "%Y-%m-%d")
        # Integer
        with contextlib.suppress(ValueError):
            value = int(value)  # type: ignore
        return value


class FilterSchema(BaseModel):
    filters_or: list[FilterItem]
    filters_and: list[FilterItem]
