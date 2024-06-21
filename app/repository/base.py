from typing import TypeVar, Generic

from sqlalchemy import select, ColumnElement, func
from sqlalchemy.exc import SQLAlchemyError

from core.models import Base
from core.db import db_helper


T = TypeVar('T', bound=Base)


class BaseRepository:

    def __init__(self, model) -> None:
        self.model = model

    async def get(self, **kwargs):
        query = select(self.model).where(*(getattr(self.model, key) == value for key, value in kwargs.items()))
        result = await db_helper.session.scalar(query)
        return result

    async def list(
        self,
        order_by: list[ColumnElement] = None,
        offset: int = None,
        limit: int = None,
        **kwargs
    ):
        stmt = select(self.model)

        if limit:
            stmt = stmt.offset(offset).limit(limit)
        stmt = stmt.where(*(getattr(self.model, key) == value for key, value in kwargs.items()))

        if order_by:
            stmt = stmt.order_by(*order_by)

        result = (await db_helper.session.scalars(stmt)).all()
        return result

    async def create(self, **kwargs):
        obj = self.model(**kwargs)
        db_helper.session.add(obj)
        #await db_helper.session.flush()
        return obj

    async def save(self, instance: Generic[T], flush: bool = False) -> Generic[T]:
        db_helper.session.add(instance)
        if flush:
            await db_helper.session.flush()
        return instance

    async def delete(self, **kwargs):
        query = select(self.model).where(*(getattr(self.model, key) == value for key, value in kwargs.items()))
        record = (await db_helper.session.scalars(query)).first()
        if record:
            await db_helper.session.delete(record)
        else:
            raise ValueError(f'Not found record with params {(getattr(self.model, key) == value for key, value in kwargs.items())}')

    async def update(self, updates: dict, filter_: dict = None, instance: Generic[T] = None) -> Generic[T]:
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
                raise AttributeError(f"Requires at least one parameter: filter_ or instance")

            # Fetch the record
            if instance is None:
                query = select(self.model).where(*(getattr(self.model, key) == value for key, value in filter_.items()))
                instance = (await db_helper.session.scalars(query)).first()

            # Apply updates
            for key, value in updates.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                else:
                    raise AttributeError(f"{key} is not a valid attribute of {self.model.__name__}")

            return instance
        except SQLAlchemyError as e:
            await db_helper.session.rollback()
            raise e

        except Exception as e:
            await db_helper.session.rollback()
            raise e

    async def count(self, by_field: ColumnElement, **kwargs):
        stmt = select(func.count(by_field)).where(*(getattr(self.model, key) == value for key, value in kwargs.items()))
        result = await db_helper.session.execute(stmt)
        count = result.scalar()
        return count
