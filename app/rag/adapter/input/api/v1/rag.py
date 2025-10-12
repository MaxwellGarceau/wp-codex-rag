from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.container import Container
from app.rag.application.dto import RAGQueryRequestDTO, RAGQueryResponseDTO
from app.rag.domain.usecase.rag import RAGUseCase
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
    usecase: RAGUseCase = Depends(Provide[Container.rag_service]),
):
    try:
        result = await usecase.query(question=request.question)
        return result
    except Exception as e:
        # This will be handled by the global exception handlers
        # but we can also add specific error handling here if needed
        raise e


@rag_router.get("/health")
async def health_check():
    """Simple health check endpoint for testing CORS without OpenAI dependency."""
    return {"status": "healthy", "message": "RAG service is running"}
