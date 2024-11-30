import datetime
from typing import Generic, Iterable, Type, TypeVar

from sqlalchemy import ColumnElement

from app.core.db.transactional import Propagation, Transactional
from app.core.exceptions.entity import FieldNotFound, RecordNotFound
from app.core.models import Base
from app.core.schemas.base import (
    CrudSchema,
    FilterSchema,
    PaddingSchema,
    SearchSchema,
    SortSchema,
)
from app.repository.base import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)
CreateSchemaType = TypeVar("CreateSchemaType", bound=CrudSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=CrudSchema)


class BaseService(Generic[ModelType, RepositoryType]):
    def __init__(self, model: Type[ModelType], repository: RepositoryType) -> None:
        self.model = model
        self.repository = repository

    async def get(
        self,
        pk: int,
        select_load: list[ColumnElement | dict[str, ColumnElement]] | None = None,
    ) -> ModelType:
        obj = await self.repository.get(select_load, id=pk)
        if obj is None:
            raise RecordNotFound
        return obj

    async def get_by_filed(
        self,
        select_load: list[ColumnElement] | None = None,
        **kwargs: str | int | datetime.datetime,
    ) -> ModelType:
        obj = await self.repository.get(select_load, **kwargs)
        if obj is None:
            raise RecordNotFound
        return obj

    async def list(
        self,
        padding: PaddingSchema,
        sort: SortSchema,
        search_data: SearchSchema | None,
        filter_: FilterSchema | None = None,
        select_load: list[ColumnElement] | None = None,
    ) -> tuple[Iterable[Type[ModelType]], int]:
        try:
            sort_field = getattr(self.model, sort.sort_field)
        except AttributeError as e:
            raise FieldNotFound from e

        objs, count = await self.repository.list(
            [sort_field],
            sort.desc,
            search_data,
            padding.offset,
            padding.limit,
            filter_,
            select_load,
            sort.sort_case_ids,
        )
        return objs, count

    @Transactional(Propagation.REQUIRED)
    async def create(self, create_schema: CreateSchemaType) -> ModelType:
        obj = self.model(**create_schema.model_dump(exclude=create_schema.extra_fields))
        await self.repository.save(obj)
        return obj

    @Transactional(Propagation.REQUIRED)
    async def update(self, pk: int, update_schema: UpdateSchemaType) -> ModelType:
        obj = await self.get(pk)
        await self.repository.update(
            update_schema.model_dump(
                exclude_defaults=True,
                exclude=update_schema.extra_fields,
            ),
            instance=obj,
        )
        return obj

    @Transactional(Propagation.REQUIRED)
    async def delete(self, pk: int) -> None:
        try:
            await self.repository.delete(id=pk)
        except ValueError as e:
            raise RecordNotFound from e
