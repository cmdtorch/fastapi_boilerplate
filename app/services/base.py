from typing import TypeVar, Generic

from pydantic import BaseModel
from sqlalchemy import ColumnElement

from core.db.transactional import Transactional, Propagation
from core.exceptions.entity import RecordNotFound, FieldNotFound
from core.models import Base
from core.schemas.base import PaddingSchema, SortSchema, SearchSchema, FilterSchema
from repository.base import BaseRepository


ModelType = TypeVar('ModelType', bound=Base)
RepositoryType = TypeVar('RepositoryType', bound=BaseRepository)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class BaseService(Generic[ModelType, RepositoryType]):

    def __init__(self, model: ModelType, repository: RepositoryType) -> None:
        self.model = model
        self.repository = repository

    async def get(self, pk: int, select_load: list[ColumnElement] | None = None) -> ModelType:
        obj = await self.repository.get(select_load, id=pk)
        if obj is None:
            raise RecordNotFound
        return obj

    async def get_by_filed(self, select_load: list[ColumnElement] | None = None, **kwargs) -> ModelType:
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
        select_load: list[ColumnElement] | None = None
    ) -> tuple[list[ModelType], int]:
        try:
            sort_field = getattr(self.model, sort.sort_field)
        except AttributeError:
            raise FieldNotFound

        if search_data is not None and search_data.search_fields is None:
            search_data = None

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
            update_schema.model_dump(exclude_defaults=True, exclude=update_schema.extra_fields),
            instance=obj,
        )
        return obj

    @Transactional(Propagation.REQUIRED)
    async def delete(self, pk: int) -> None:
        try:
            await self.repository.delete(id=pk)
        except ValueError:
            raise RecordNotFound

