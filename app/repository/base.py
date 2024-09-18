from typing import TypeVar

from sqlalchemy import desc, asc, and_, case
from sqlalchemy import select, ColumnElement, func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from core.models import Base
from core.db import db_helper
from core.schemas.base import SearchSchema, FilterSchema

T = TypeVar('T', bound=Base)


class BaseRepository:

    def __init__(self, model) -> None:
        self.model = model

    async def get(self, select_load: list[ColumnElement] | None = None, **kwargs) -> T:
        """
        Get object by params
        :param select_load: Columns list for select on load
        :param kwargs: list of params for filtering
        :return: Object
        """
        query = select(self.model).where(*(getattr(self.model, key) == value for key, value in kwargs.items()))
        if select_load:
            query = query.options(
                *(selectinload(model) for model in select_load),
            )
        result = await db_helper.session.scalar(query)
        return result

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
        **kwargs
    ) -> list[T]:
        """
        Get list of objects
        :param order_by: List of column for ordering
        :param order_desc: Boolean value for desc or asc ordering
        :param search: search schema for filtering
        :param offset: offset on list
        :param limit: limit of list
        :param filter_: A dictionary of filter for record (can be none if the instance is installed)
        :param select_load: Columns list for select on load
        :param sort_case_ids: Sort by list of ids
        :return: List of objects, total count of objects (without limit)
        """
        stmt = select(self.model)
        count_stmt = select(func.count(self.model.id))

        stmt = stmt.where(*(getattr(self.model, key) == value for key, value in kwargs.items()))
        count_stmt = count_stmt.where(*(getattr(self.model, key) == value for key, value in kwargs.items()))

        if filter_ and filter_.filters_or:
            stmt = stmt.where(
                or_(
                    *(getattr(self.model, f.name) == f.value for f in filter_.filters_or)  # type: ignore
                )
            )
            count_stmt = count_stmt.where(
                or_(
                    *(getattr(self.model, f.name) == f.value for f in filter_.filters_or)  # type: ignore
                )
            )

        if filter_ and filter_.filters_and:
            stmt = stmt.where(
                and_(
                    *(getattr(self.model, f.name) == f.value for f in filter_.filters_and)  # type: ignore
                )
            )
            count_stmt = count_stmt.where(
                and_(
                    *(getattr(self.model, f.name) == f.value for f in filter_.filters_and)  # type: ignore
                )
            )

        if search:
            stmt = stmt.where(
                or_(
                    (getattr(self.model, field).contains(search.query) for field in search.search_fields)  # type: ignore
                )
            )
            count_stmt = count_stmt.where(
                or_(
                    (getattr(self.model, field).contains(search.query) for field in search.search_fields)  # type: ignore
                )
            )

        if select_load:
            stmt = stmt.options(
                *(selectinload(model) for model in select_load),
            )

        if limit:
            stmt = stmt.offset(offset).limit(limit)

        if sort_case_ids:
            case_conditions = [(self.model.id == id_, index) for index, id_ in enumerate(sort_case_ids)]
            case_stmt = case(*case_conditions, else_=len(sort_case_ids))
            stmt = stmt.order_by(case_stmt)

        if order_by:
            sort_type = desc if order_desc else asc
            stmt = stmt.order_by(sort_type(*order_by))

        result = (await db_helper.session.scalars(stmt)).all()

        # Count
        count_result = await db_helper.session.execute(count_stmt)
        count = count_result.scalar()

        return result, count

    async def create(self, **kwargs) -> T:
        obj = self.model(**kwargs)
        db_helper.session.add(obj)
        #await db_helper.session.flush()
        return obj

    async def save(self, instance: T, flush: bool | None = False) -> T:
        db_helper.session.add(instance)
        if flush:
            await db_helper.session.flush()
        return instance

    async def delete(self, **kwargs) -> None:
        query = select(self.model).where(*(getattr(self.model, key) == value for key, value in kwargs.items()))
        record = (await db_helper.session.scalars(query)).first()
        if record:
            await db_helper.session.delete(record)
        else:
            raise ValueError(f'Not found record with params {(getattr(self.model, key) == value for key, value in kwargs.items())}')

    async def update(self, updates: dict, filter_: dict | None = None, instance: T | None = None) -> T:
        """
        Updates an existing record.
        :param updates: A dictionary of update
        :param filter_: A dictionary of filter for record (can be none if the instance is installed)
        :param instance: Instance for update (if instance is none, get from db)
        :return: The updated model instance
        :raises: Exception if the update fails
        """
        try:
            if filter_ is None and instance is None:
                raise AttributeError("Requires at least one parameter: filter_ or instance")

            # Fetch the record
            if instance is None and filter_:
                query = select(self.model).where(*(getattr(self.model, key) == value for key, value in filter_.items()))
                instance = (await db_helper.session.scalars(query)).first()

            # Apply updates
            for key, value in updates.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                else:
                    raise AttributeError(f"{key} is not a valid attribute of {self.model.__name__}")

            return instance  # type: ignore
        except SQLAlchemyError as e:
            await db_helper.session.rollback()
            raise e

        except Exception as e:
            await db_helper.session.rollback()
            raise e

    async def count(self, by_field: ColumnElement, **kwargs) -> int:
        stmt = select(func.count(by_field)).where(*(getattr(self.model, key) == value for key, value in kwargs.items()))
        result = await db_helper.session.execute(stmt)
        count = result.scalar()
        return count
