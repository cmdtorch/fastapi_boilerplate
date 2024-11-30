from enum import Enum
from functools import wraps
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar

from app.core.db import db_helper


class Propagation(Enum):
    REQUIRED = "required"
    REQUIRED_NEW = "required_new"


P = ParamSpec("P")
R = TypeVar("R")


class Transactional:
    def __init__(self, propagation: Propagation = Propagation.REQUIRED) -> None:
        self.propagation = propagation

    def __call__(
        self, function: Callable[P, Coroutine[Any, Any, R]]
    ) -> Callable[P, Coroutine[Any, Any, R]]:
        @wraps(function)
        async def decorator(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                if self.propagation == Propagation.REQUIRED:
                    result = await self._run_required(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
                elif self.propagation == Propagation.REQUIRED_NEW:
                    result = await self._run_required_new(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
                else:
                    result = await self._run_required(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
            except Exception as e:
                await db_helper.session.rollback()
                raise e

            return result

        return decorator

    async def _run_required(
        self,
        function: Callable[P, Coroutine[Any, Any, R]],
        args: P.args,
        kwargs: P.kwargs,
    ) -> R:
        result = await function(*args, **kwargs)
        await db_helper.session.commit()
        return result

    async def _run_required_new(
        self,
        function: Callable[P, Coroutine[Any, Any, R]],
        args: P.args,
        kwargs: P.kwargs,
    ) -> R:
        db_helper.session.begin()
        result = await function(*args, **kwargs)
        await db_helper.session.commit()
        return result
