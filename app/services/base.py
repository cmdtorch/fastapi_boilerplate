import datetime
from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import ColumnElement

from app.core.db.transactional import Propagation, Transactional
from app.core.exceptions.entity import RecordNotFound
from app.models import Base
from app.repository.base import BaseRepository
from app.schemas.base import CrudSchema, PaginationGetter

ModelType = TypeVar("ModelType", bound=Base)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)  # type: ignore
CreateSchemaType = TypeVar("CreateSchemaType", bound=CrudSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=CrudSchema)


class BaseService(Generic[ModelType, RepositoryType]):
    def __init__(self, model: Type[ModelType], repository: RepositoryType) -> None:
        self.model = model
        self.repository = repository

    async def get(
        self,
        select_load: list[ColumnElement] | None = None,
        **kwargs: str | int | datetime.datetime | UUID,
    ) -> ModelType:
        """
        Get an object by its primary key or other fields.
        If the object is not found, a RecordNotFound exception is raised.
        :param select_load: Optional list of columns to load.
        :param kwargs: Additional fields to filter the object.
        :return: The object if found.
        """
        obj = await self.repository.get(select_load, **kwargs)  # type: ignore
        if obj is None:
            raise RecordNotFound
        return obj

    async def list(
        self,
        padding: PaginationGetter,
        order_by: list[ColumnElement] | None = None,
        order_by_desc: bool = False,
        select_load: list[ColumnElement] | None = None,
        **kwargs: str | int | datetime.datetime | UUID,
    ) -> tuple[list[Type[ModelType]], int]:
        """
        List objects with pagination and optional sorting.
        :param padding: Pagination object containing offset and limit.
        :param order_by: Optional list of columns to sort by.
        :param order_by_desc: Boolean indicating if sorting should be descending.
        :param select_load: Optional list of columns to load.
        :param kwargs: Additional fields to filter the objects.
        :return: A tuple containing a list of objects and the total count.
        """
        objs, count = await self.repository.list(
            order_by,
            order_by_desc,
            padding.offset,
            padding.limit,
            select_load,
            **kwargs,
        )
        return objs, count

    @Transactional(Propagation.REQUIRED)
    async def create(self, create_schema: CreateSchemaType, **kwargs: Any) -> ModelType:
        obj = self.model(**create_schema.model_dump(), **kwargs)
        await self.repository.save(obj)
        return obj

    @Transactional(Propagation.REQUIRED)
    async def update(
        self, pk: int | UUID, update_schema: UpdateSchemaType
    ) -> ModelType:
        obj = await self.get(id=pk)
        await self.repository.update(
            update_schema.model_dump(
                exclude=update_schema.extra_fields
                if hasattr(update_schema, "extra_fields")
                else None,
            ),
            id=obj.id,
        )
        return obj

    @Transactional(Propagation.REQUIRED)
    async def delete(self, pk: int | UUID) -> None:
        try:
            await self.repository.delete(id=pk)
        except ValueError as e:
            raise RecordNotFound from e
