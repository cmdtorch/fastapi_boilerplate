from collections.abc import AsyncGenerator
from contextvars import ContextVar, Token

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

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
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_recycle=3600,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        self.session: AsyncSession | async_scoped_session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=get_session_id,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

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
