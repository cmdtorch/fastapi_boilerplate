import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.responses import JSONResponse

from app.api import router as api_router
from app.api.v1.mock_auth import main_route
from app.core.config import settings
from app.core.dependencies.logging import Logging
from app.core.exceptions.base import CustomException
from app.core.middlewares.sqlalchemy import SQLAlchemyMiddleware


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
    async def custom_exception_handler(
        _: Request,
        exc: CustomException,
    ) -> JSONResponse:
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
