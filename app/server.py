from fastapi import Depends, FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.container import Container
from app.rag.adapter.input.api import router as rag_router
from core.config import config
from core.exceptions import CustomException
from core.exceptions.handlers import register_exception_handlers
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    AuthBackend,
    AuthenticationMiddleware,
    ResponseLogMiddleware,
)
from core.helpers.cache import Cache, CustomKeyMaker, RedisBackend
from core.logging_config import setup_logging


def init_routers(app_: FastAPI) -> None:
    container = Container()
    rag_router.container = container
    app_.include_router(rag_router)


def init_listeners(app_: FastAPI) -> None:
    """Initialize exception handlers and other app listeners."""
    register_exception_handlers(app_)


def on_auth_error(request: Request, exc: Exception) -> JSONResponse:
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


def make_middleware() -> list[Middleware]:
    # Parse CORS origins from config
    cors_origins = config.CORS_ORIGINS.split(",") if config.CORS_ORIGINS else []

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=AuthBackend(),
            on_error=on_auth_error,
        ),
        Middleware(ResponseLogMiddleware),
    ]
    return middleware


def init_cache() -> None:
    Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())


def create_app() -> FastAPI:
    # Initialize logging configuration
    setup_logging()

    app_ = FastAPI(
        title="Hide",
        description="Hide API",
        version="1.0.0",
        docs_url=None if config.ENV == "production" else "/docs",
        redoc_url=None if config.ENV == "production" else "/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)
    init_cache()
    return app_


app = create_app()
