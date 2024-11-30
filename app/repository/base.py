import datetime
from collections.abc import Iterable
from typing import Any, Callable, TypeVar

from sqlalchemy import (
    Case,
    ColumnElement,
    Select,
    and_,
    asc,
    case,
    desc,
    func,
    or_,
    select,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.core.db import db_helper
from app.core.models import Base
from app.core.schemas.base import FilterItem, FilterSchema, SearchItem, SearchSchema

T = TypeVar("T", bound=Base)


class BaseFilter:
    def apply(self, stmt: Select, model: Base) -> Select:
        """Method to apply the filter to the query."""
        raise NotImplementedError


class ConditionFilter(BaseFilter):
    def __init__(
        self,
        filters: list[FilterItem],
        condition: Callable[[Any], None],
    ) -> None:
        self.filters = filters
        self.condition = condition

    def apply(self, stmt: Select, model: type[Base]) -> Select:
        conditions = []
        for f in self.filters:
            if isinstance(f.value, FilterItem):
                related_model = getattr(model, f.name).property.mapper.class_
                if getattr(model, f.name).property.uselist:
                    conditions.append(
                        getattr(model, f.name).any(
                            getattr(related_model, f.value.name) == f.value.value,
                        ),
                    )
                else:
                    conditions.append(
                        getattr(model, f.name).has(
                            getattr(related_model, f.value.name) == f.value.value,
                        ),
                    )
            else:
                conditions.append(getattr(model, f.name) == f.value)
        return stmt.where(self.condition(*conditions))


class SearchFilter(BaseFilter):
    def __init__(self, search: SearchSchema) -> None:
        self.search = search

    def apply(self, stmt: Select, model: type[Base]) -> Select:
        if not self.search or not self.search.search:
            return stmt
        search_conditions = []
        for s in self.search.search:
            if isinstance(s.value, SearchItem):
                related_model = getattr(model, s.name).property.mapper.class_
                search_conditions.append(
                    getattr(related_model, s.value.name).contains(s.value.value),
                )
            else:
                search_conditions.append(getattr(model, s.name).contains(s.value))
        return stmt.where(or_(*search_conditions)).distinct()


class BaseRepository:
    def __init__(self, model: type[Base]) -> None:
        self.model = model

    async def get(
        self,
        select_load: list[ColumnElement | dict[str, ColumnElement]] | None = None,
        **kwargs: str | int | datetime.datetime,
    ) -> Base:
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
        return await db_helper.session.scalar(query)

    async def list(
        self,
        order_by: list[ColumnElement] | None = None,
        order_desc: bool = True,
        search: SearchSchema | None = None,
        offset: int | None = None,
        limit: int | None = None,
        filter_: FilterSchema | None = None,
        select_load: list[ColumnElement] | None = None,
        sort_case_ids: list[int] | None = None,
        **kwargs: str | int | datetime.datetime,
    ) -> tuple[Iterable[Base], int]:
        stmt = select(self.model)
        stmt = stmt.where(
            *(getattr(self.model, key) == value for key, value in kwargs.items()),
        )

        # Apply OR filters if they exist
        if filter_ and filter_.filters_or:
            stmt = ConditionFilter(filter_.filters_or, or_).apply(stmt, self.model)

        # Apply AND filters if they exist
        if filter_ and filter_.filters_and:
            stmt = ConditionFilter(filter_.filters_and, and_).apply(stmt, self.model)

        # Apply Search filter
        if search:
            stmt = SearchFilter(search).apply(stmt, self.model)

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

        if limit:
            stmt = stmt.offset(offset).limit(limit)

        if sort_case_ids:
            case_conditions = [
                (self.model.id == id_, index) for index, id_ in enumerate(sort_case_ids)
            ]
            case_stmt: Case = case(*case_conditions, else_=len(sort_case_ids))
            stmt = stmt.order_by(case_stmt)

        if order_by:
            sort_type = desc if order_desc else asc
            stmt = stmt.order_by(sort_type(*order_by))

        result = (await db_helper.session.scalars(stmt)).all()

        # Count
        count_result = await db_helper.session.execute(count_stmt)
        count = count_result.scalar()

        return result, count

    async def create(self, **kwargs: str | int | datetime.datetime) -> Base:
        obj = self.model(**kwargs)
        db_helper.session.add(obj)
        return obj

    async def save(self, instance: T, flush: bool | None = False) -> T:
        db_helper.session.add(instance)
        if flush:
            await db_helper.session.flush()
        return instance

    async def delete(self, **kwargs: str | int | datetime.datetime) -> None:
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
        updates: dict[str, str | int | datetime.datetime],
        filter_: dict[str, str | int | datetime.datetime] | None = None,
        instance: T | None = None,
    ) -> T:
        """
        Updates an existing record.
        :param updates: A dictionary of update
        :param filter_: A dictionary of filter for record
        (can be none if the instance is installed)
        :param instance: Instance for update (if instance is none, get from db)
        :return: The updated model instance
        :raises: Exception if the update fails
        """
        try:
            if filter_ is None and instance is None:
                raise AttributeError(
                    "Requires at least one parameter: filter_ or instance",
                )

            # Fetch the record
            if instance is None and filter_:
                query = select(self.model).where(
                    *(
                        getattr(self.model, key) == value
                        for key, value in filter_.items()
                    ),
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

            return instance  # type: ignore
        except SQLAlchemyError as e:
            await db_helper.session.rollback()
            raise e

        except Exception as e:  # type: ignore
            await db_helper.session.rollback()
            raise e

    async def count(
        self,
        by_field: ColumnElement,
        **kwargs: str | int | datetime.datetime,
    ) -> int:
        stmt = select(func.count(by_field)).where(
            *(getattr(self.model, key) == value for key, value in kwargs.items()),
        )
        result = await db_helper.session.execute(stmt)
        return result.scalar()
