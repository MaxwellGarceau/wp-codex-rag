from fastapi import Depends, FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import RateLimitError, APIError

from app.auth.adapter.input.api import router as auth_router
from app.container import Container
from app.user.adapter.input.api import router as user_router
from app.rag.adapter.input.api import router as rag_router
from core.config import config
from core.dto.error_response import ErrorResponse
from core.exceptions import CustomException
from core.helpers.error_responses import create_error_response_from_exception
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    AuthBackend,
    AuthenticationMiddleware,
    ResponseLogMiddleware,
    SQLAlchemyMiddleware,
)
from core.helpers.cache import Cache, CustomKeyMaker, RedisBackend


def init_routers(app_: FastAPI) -> None:
    container = Container()
    user_router.container = container
    auth_router.container = container
    app_.include_router(user_router)
    app_.include_router(auth_router)
    rag_router.container = container
    app_.include_router(rag_router)


def init_listeners(app_: FastAPI) -> None:
    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )
    
    # OpenAI API error handlers
    @app_.exception_handler(RateLimitError)
    async def rate_limit_handler(request: Request, exc: RateLimitError):
        return create_error_response_from_exception(
            status_code=429,
            exception=exc,
            error_type="rate_limit"
        )
    
    @app_.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        return create_error_response_from_exception(
            status_code=500,
            exception=exc,
            error_type="api_error"
        )


def on_auth_error(request: Request, exc: Exception):
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
        Middleware(SQLAlchemyMiddleware),
        Middleware(ResponseLogMiddleware),
    ]
    return middleware


def init_cache() -> None:
    Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())


def create_app() -> FastAPI:
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
