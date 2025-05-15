import asyncio
from pathlib import Path
from typing import AsyncGenerator, Callable, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from alembic import command  # type: ignore[attr-defined]
from alembic.config import Config as AlembicConfig
from app.core.config import settings
from app.core.db.db_helper import DatabaseHelper
from app.core.utils.token import TokenHelper
from app.main import app
from app.models import User


@pytest.fixture(scope="session")
def test_db_helper() -> DatabaseHelper:
    return DatabaseHelper(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
    )


@pytest.fixture(scope="session")
def async_session_maker(test_db_helper: DatabaseHelper) -> Callable[[], AsyncSession]:
    return async_sessionmaker(test_db_helper.engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def alembic_conf() -> AlembicConfig:
    project_dir = Path(__file__).resolve().parent.parent
    config_path = Path.joinpath(project_dir, "alembic.ini")
    migration_path = Path.joinpath(project_dir, "alembic")
    alembic_config = AlembicConfig(Path(config_path))
    alembic_config.set_main_option("sqlalchemy.url", str(settings.db.url))
    alembic_config.set_main_option("script_location", str(migration_path))
    return alembic_config


@pytest.fixture(autouse=True, scope="session")
def prepare_database(alembic_conf: AlembicConfig) -> Generator[None, None, None]:
    command.upgrade(alembic_conf, "head")
    yield
    command.downgrade(alembic_conf, "base")


@pytest.fixture(scope="session")
def event_loop(
    request: pytest.FixtureRequest,
) -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def test_consumer_access_token(test_user_consumer: User) -> str:
    # Generate token for the user
    return TokenHelper.access_token(test_user_consumer.email)
