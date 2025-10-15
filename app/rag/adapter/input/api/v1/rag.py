from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.container import Container
from app.rag.application.dto import RAGQueryRequestDTO, RAGQueryResponseDTO
from app.rag.application.handler.llm_only_handler import LLMOnlyHandler
from app.rag.application.handler.rag_handler import RAGHandler
from app.rag.application.service.llm_service_factory import LLMServiceFactory
from core.dto.error_response import ErrorResponse

rag_router = APIRouter()


@rag_router.post(
    "/query",
    response_model=RAGQueryResponseDTO,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
@inject
async def query_rag(
    request: RAGQueryRequestDTO,
    llm_service_factory: LLMServiceFactory = Depends(
        Provide[Container.llm_service_factory]
    ),
):
    """Query endpoint that uses RAG (vector DB + LLM) for enhanced responses."""
    handler = RAGHandler(llm_service_factory)
    return await handler.handle_query(request)


@rag_router.post(
    "/query-llm-only",
    response_model=RAGQueryResponseDTO,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
@inject
async def query_llm_only(
    request: RAGQueryRequestDTO,
    llm_service_factory: LLMServiceFactory = Depends(
        Provide[Container.llm_service_factory]
    ),
):
    """Query endpoint that uses only LLM without RAG context for comparison."""
    handler = LLMOnlyHandler(llm_service_factory)
    return await handler.handle_query(request)


@rag_router.get("/health")
async def health_check():
    """Simple health check endpoint for testing CORS without OpenAI dependency."""
    return {"status": "healthy", "message": "RAG service is running"}
