from fastapi import Depends, FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from app.container import Container
from app.rag.adapter.input.api import router as rag_router
from core.config import config
from core.exceptions.handlers import register_exception_handlers
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    ResponseLogMiddleware,
)
from core.logging_config import setup_logging


def init_routers(app_: FastAPI) -> None:
    container = Container()
    rag_router.container = container
    app_.include_router(rag_router)


def init_listeners(app_: FastAPI) -> None:
    """Initialize exception handlers and other app listeners."""
    register_exception_handlers(app_)




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
        Middleware(ResponseLogMiddleware),
    ]
    return middleware




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
    return app_


app = create_app()
