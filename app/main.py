import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from core.config import settings
from api import router as api_router
from api.api_v1.mock_auth import main_route
from core.dependencies.logging import Logging
from core.exceptions.base import CustomException
from core.middlewares.sqlalchemy import SQLAlchemyMiddleware
from core.models import db_helper


# If you use sentry install sentry_sdk and uncomment code below
# if not settings.debug and settings.sentry.dsn:
#     sentry_sdk.init(
#         dsn=settings.sentry.dsn,
#         traces_sample_rate=settings.sentry.traces_sample_rate,
#         profiles_sample_rate=settings.sentry.profiles_sample_rate,
#     )


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    # startup
    yield
    # shutdown
    await db_helper.dispose()


def set_cors(fastapi_app: FastAPI) -> None:
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def set_middlewares(fastapi_app: FastAPI) -> None:
    fastapi_app.add_middleware(SQLAlchemyMiddleware)


def set_routers(fastapi_app: FastAPI) -> None:
    fastapi_app.include_router(api_router)
    if settings.debug:
        fastapi_app.include_router(main_route)


def set_listeners(fastapi_app: FastAPI) -> None:
    # Exception handler
    @fastapi_app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )


def init_app() -> FastAPI:
    fastapi_app = FastAPI(
        title=settings.info.name,
        description=settings.info.description,
        version=settings.info.version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        debug=settings.debug,
        dependencies=[Depends(Logging)],
    )
    set_routers(fastapi_app)
    set_cors(fastapi_app)
    set_listeners(fastapi_app)
    set_middlewares(fastapi_app)
    return fastapi_app


app = init_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.debug,
    )
