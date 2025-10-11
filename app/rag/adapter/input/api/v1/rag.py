from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.container import Container
from app.rag.application.dto import RAGQueryRequestDTO, RAGQueryResponseDTO
from app.rag.domain.usecase.rag import RAGUseCase


rag_router = APIRouter()


@rag_router.post("/query", response_model=RAGQueryResponseDTO)
@inject
async def query_rag(
    request: RAGQueryRequestDTO,
    usecase: RAGUseCase = Depends(Provide[Container.rag_service]),
):
    result = await usecase.query(question=request.question)
    return result


@rag_router.get("/health")
async def health_check():
    """Simple health check endpoint for testing CORS without OpenAI dependency."""
    return {"status": "healthy", "message": "RAG service is running"}
