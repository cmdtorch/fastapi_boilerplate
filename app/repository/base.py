import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import (
    ColumnElement,
    asc,
    desc,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import db_helper
from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def get(
        self,
        select_load: list[ColumnElement | dict[str, ColumnElement]] | None = None,
        session: AsyncSession | None = None,
        **kwargs: Any,
    ) -> ModelType | None:
        query = select(self.model).where(
            *(getattr(self.model, key) == value for key, value in kwargs.items()),
        )
        if select_load:
            options = []
            for column in select_load:
                if isinstance(column, dict):
                    options.append(
                        selectinload(column["related"]).options(
                            selectinload(column["sub_related"]),
                        ),
                    )
                else:
                    options.append(selectinload(column))
            query = query.options(
                *options,
            )
        if session:
            return await session.scalar(query)
        return await db_helper.session.scalar(query)

    async def list(
        self,
        order_by: list[ColumnElement] | None = None,
        order_desc: bool = True,
        offset: int | None = None,
        limit: int | None = None,
        select_load: list[ColumnElement] | None = None,
        **kwargs: str | int | datetime.datetime | UUID,
    ) -> tuple[list[ModelType], int]:
        stmt = select(self.model)
        stmt = stmt.where(
            *(getattr(self.model, key) == value for key, value in kwargs.items()),
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())

        if select_load:
            options = []
            for column in select_load:
                if isinstance(column, dict):
                    options.append(
                        selectinload(column["related"]).options(
                            selectinload(column["sub_related"]),
                        ),
                    )
                else:
                    options.append(selectinload(column))

            stmt = stmt.options(
                *options,
            )

        if limit and offset:
            stmt = stmt.offset(offset).limit(limit)

        if order_by:
            sort_type = desc if order_desc else asc
            stmt = stmt.order_by(
                sort_type(order_by[0]), *(desc(o) for o in order_by[1:])
            )

        result = (await db_helper.session.scalars(stmt)).all()

        # Count
        count_result = await db_helper.session.execute(count_stmt)
        count = count_result.scalar()

        return result, count

    async def create(self, **kwargs: str | int | UUID | datetime.datetime) -> Base:
        obj = self.model(**kwargs)
        db_helper.session.add(obj)
        return obj

    async def save(
        self,
        instance: ModelType,
        session: AsyncSession | None = None,
        flush: bool | None = False,
    ) -> ModelType:
        session_ = session if session else db_helper.session
        session_.add(instance)
        if flush:
            await session_.flush()
        if session:
            await session_.commit()
        return instance

    async def delete(self, **kwargs: str | int | UUID | datetime.datetime) -> None:
        query = select(self.model).where(
            *(getattr(self.model, key) == value for key, value in kwargs.items()),
        )
        record = (await db_helper.session.scalars(query)).first()
        if record:
            await db_helper.session.delete(record)
        else:
            raise ValueError(
                f"Not found record with params "
                f"{(f"{key} = {value}" for key, value in kwargs.items())}",
            )

    async def update(
        self,
        updates: dict[str, Any],
        **kwargs: Any,
    ) -> ModelType:
        """
        Updates an existing record.
        :param updates: A dictionary of update
        **kwargs: Key-value pairs corresponding to the fields and
         their updated values in the model.
        :return: The updated model instance
        """

        query = select(self.model).where(
            *(getattr(self.model, key) == value for key, value in kwargs.items()),
        )
        instance = (await db_helper.session.scalars(query)).first()

        # Apply updates
        for key, value in updates.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
            else:
                raise AttributeError(
                    f"{key} is not a valid attribute of {self.model.__name__}",
                )
        return instance

    async def count(
        self,
        by_field: ColumnElement,
        **kwargs: str | int | datetime.datetime | UUID,
    ) -> int:
        stmt = select(func.count(by_field)).where(
            *(getattr(self.model, key) == value for key, value in kwargs.items()),
        )
        result = await db_helper.session.execute(stmt)
        return result.scalar()
