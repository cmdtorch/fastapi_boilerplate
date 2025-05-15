from collections.abc import AsyncGenerator
from contextvars import ContextVar, Token

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, Pool

from app.core.config import settings

session_context: ContextVar[str] = ContextVar("session_context")


def get_session_id() -> str:
    return session_context.get()


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_recycle: int = 3600,
        pool_class: Pool | None = None,
    ) -> None:
        self.url = url
        self.echo = echo
        self.echo_pool = echo_pool
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_recycle = pool_recycle
        self.pool_class = pool_class

        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._scoped_session: AsyncSession | async_scoped_session | None = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            engine_kwargs = {
                "url": self.url,
                "echo": self.echo,
                "echo_pool": self.echo_pool,
                "pool_size": self.pool_size,
                "max_overflow": self.max_overflow,
                "pool_recycle": self.pool_recycle,
                "poolclass": self.pool_class,
            }

            # Remove pool_recycle, if pool_class isNullPool
            if self.pool_class is NullPool:
                engine_kwargs.pop("pool_size", None)
                engine_kwargs.pop("max_overflow", None)

            self._engine = create_async_engine(**engine_kwargs)
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
            )
        return self._session_factory

    @property
    def session(self) -> AsyncSession | async_scoped_session:
        if self._scoped_session is None:
            self._scoped_session = async_scoped_session(
                session_factory=self.session_factory,
                scopefunc=get_session_id,
            )
        return self._scoped_session

    async def dispose(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

    def set_session_context(self, session_id: str) -> Token:  # type: ignore
        return session_context.set(session_id)

    def reset_session_context(self, context: Token) -> None:  # type: ignore
        session_context.reset(context)


db_helper = DatabaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)

celery_db_helper = DatabaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_class=NullPool,
)
