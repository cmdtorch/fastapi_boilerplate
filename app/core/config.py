from pydantic import BaseModel, PostgresDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class InfoConfig(BaseModel):
    name: str = "FastAPI"
    version: str = "0.1.0"
    description: str = "FastAPI project"


class RunConfig(BaseModel):
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    user: str = "/user"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class AuthConfig(BaseModel):
    access_token_time: int = 900
    refresh_token_time: int = 15_000_000
    secret_key: str = "YOUR_SECRET_KEY"
    algorithm: str = "HS256"
    debug_password: str = "123456"


class SentryConfig(BaseModel):
    dsn: str | None = None
    traces_sample_rate: float = 1.0
    profiles_sample_rate: float = 1.0


class PaginationConfig(BaseModel):
    requests_count: int = 10


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    debug: bool = False

    info: InfoConfig = InfoConfig()
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    auth: AuthConfig = AuthConfig()
    sentry: SentryConfig = SentryConfig()
    pagination: PaginationConfig = PaginationConfig()


settings = Settings()  # type: ignore
