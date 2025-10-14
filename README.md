# RAG: WordPress Codex Q&A

## Overview
This app adds a Retrieval-Augmented Generation (RAG) pipeline using Chroma and Groq to answer WordPress questions. It ingests WordPress Codex content (plugin development scope) into a vector store, retrieves relevant chunks, and forwards enriched prompts to an LLM.

## Setup
- Ensure Python dependencies are installed via Poetry
- Create a `.env` (see `.env.example`) and set `GROQ_API_KEY`
- Optional: adjust `CHROMA_PERSIST_DIRECTORY`, `RAG_COLLECTION_NAME`

## Ingestion
```shell
poetry run python scripts/ingest_wp_codex.py --section plugin
```
This fetches WordPress docs and stores embeddings in Chroma under the configured collection.

## API Endpoint
- `POST /api/v1/rag/query` with body `{ "question": "..." }`
- Returns `{ "answer": "...", "sources": [ {"title":..., "url":...} ] }`

## Frontend
A Next.js 14 app in `frontend/` provides a minimal chat-like UI to submit questions to the backend.

### Frontend dev
```bash
cd frontend
npm install
npm run dev
```
Set `NEXT_PUBLIC_API_BASE_URL` in your frontend environment when needed.

### Environment
Backend uses variables in `core/config.py`. Create `.env` based on the following:

- `GROQ_API_KEY`: Your Groq API key
- `CHROMA_PERSIST_DIRECTORY`: Directory for Chroma persistence (mount a volume in prod)
- `RAG_COLLECTION_NAME`: Defaults to `wp_codex_plugin`

Frontend:
- `NEXT_PUBLIC_API_BASE_URL`: Base URL for backend (e.g., `http://localhost:8000`)

## Deployment
- Frontend: deploy `frontend/` to Vercel. Set `NEXT_PUBLIC_API_BASE_URL` to your backend URL.
- Backend: deploy FastAPI to Railway/Render. Persist Chroma by mounting a volume at `CHROMA_PERSIST_DIRECTORY`.

# FastAPI Boilerplate (modified)

# Features
- RAG (Retrieval-Augmented Generation) for WordPress Codex
- ChromaDB vector database
- OpenAI and HuggingFace LLM support
- Celery
- Hot reload (local development)
- Event dispatcher
- Cache

## Development Workflow

TLDR: After installing dependencies start project by running docker container for DB/Cache and run the python server for FastAPI BE.

```shell
poetry run docker-up
poetry run start
```

This project uses a **hybrid approach** for development:
- **Docker**: Runs Redis cache and ChromaDB vector database services
- **Local**: Runs the FastAPI application for faster development and debugging

### Start Docker Services (Redis + ChromaDB)
```shell
> poetry run docker-up
# or manually:
> docker-compose -f docker/docker-compose.yml up redis chromadb
```

### Install Dependencies
```shell
> poetry install
```


### Start Development Server
```shell
> poetry run start
# or manually:
> poetry run python main.py --env local --debug
```

### Run test codes
```shell
> make test
```

### Make coverage report
```shell
> make cov
```

### Formatting

```shell
> pre-commit
```

### Code Quality (Linting & Formatting)

This project uses Ruff (linter), Black (formatter), and MyPy (type checker) for code quality:

```shell
# Run all quality checks
make quality

# Auto-fix issues
make fix

# Individual commands
make lint          # Check code quality
make format        # Format code
make type-check    # Check types
```

Pre-commit hooks automatically run these checks before commits.

## RAG System

This application uses a Retrieval-Augmented Generation (RAG) system to answer questions about WordPress plugin development using the WordPress Codex documentation.

### Vector Database
- Uses ChromaDB for storing and retrieving document embeddings
- Documents are processed and embedded using OpenAI's text-embedding-3-small model
- Similarity search is performed to find relevant documentation sections

### LLM Integration
- Supports both OpenAI and HuggingFace models
- Uses OpenAI's GPT-4o-mini for generating responses
- Configurable through environment variables

## Authentication

```python
from fastapi import Request


@home_router.get("/")
def home(request: Request):
    return request.user.id
```

**Note. you have to pass jwt token via header like `Authorization: Bearer 1234`**

Custom user class automatically decodes header token and store user information into `request.user`

If you want to modify custom user class, you have to update below files.

1. `core/fastapi/schemas/current_user.py`
2. `core/fastapi/middlewares/authentication.py`

### CurrentUser

```python
class CurrentUser(BaseModel):
    id: int = Field(None, description="ID")
```

Simply add more fields based on your needs.

### AuthBackend

```python
current_user = CurrentUser()
```

After line 18, assign values that you added on `CurrentUser`.

## Top-level dependency

**Note. Available from version 0.62 or higher.**

Set a callable function when initialize FastAPI() app through `dependencies` argument.

Refer `Logging` class inside of `core/fastapi/dependencies/logging.py`

## Dependencies for specific permissions

Permissions `IsAdmin`, `IsAuthenticated`, `AllowAll` have already been implemented.

```python
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAdmin,
)


user_router = APIRouter()


@user_router.get(
    "",
    response_model=List[GetUserListResponseSchema],
    response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAdmin]))],  # HERE
)
async def get_user_list(
    limit: int = Query(10, description="Limit"),
    prev: int = Query(None, description="Prev ID"),
):
    pass
```
Insert permission through `dependencies` argument.

If you want to make your own permission, inherit `BasePermission` and implement `has_permission()` function.

**Note. In order to use swagger's authorize function, you must put `PermissionDependency` as an argument of `dependencies`.**

## Event dispatcher

Refer the README of https://github.com/teamhide/fastapi-event

## Cache

### Caching by prefix
```python
from core.helpers.cache import Cache


@Cache.cached(prefix="get_user", ttl=60)
async def get_user():
    ...
```

### Caching by tag
```python
from core.helpers.cache import Cache, CacheTag


@Cache.cached(tag=CacheTag.GET_USER_LIST, ttl=60)
async def get_user():
    ...
```

Use the `Cache` decorator to cache the return value of a function.

Depending on the argument of the function, caching is stored with a different value through internal processing.

### Custom Key builder

```python
from core.helpers.cache.base import BaseKeyMaker


class CustomKeyMaker(BaseKeyMaker):
    async def make(self, function: Callable, prefix: str) -> str:
        ...
```

If you want to create a custom key, inherit the BaseKeyMaker class and implement the make() method.

### Custom Backend

```python
from core.helpers.cache.base import BaseBackend


class RedisBackend(BaseBackend):
    async def get(self, key: str) -> Any:
        ...

    async def set(self, response: Any, key: str, ttl: int = 60) -> None:
        ...

    async def delete_startswith(self, value: str) -> None:
        ...
```

If you want to create a custom key, inherit the BaseBackend class and implement the `get()`, `set()`, `delete_startswith()` method.

Pass your custom backend or keymaker as an argument to init. (`/app/server.py`)

```python
def init_cache() -> None:
    Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())
```

### Remove all cache by prefix/tag

```python
from core.helpers.cache import Cache, CacheTag


await Cache.remove_by_prefix(prefix="get_user_list")
await Cache.remove_by_tag(tag=CacheTag.GET_USER_LIST)
```
