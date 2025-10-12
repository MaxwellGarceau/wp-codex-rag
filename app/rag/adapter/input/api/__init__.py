from fastapi import APIRouter

from app.rag.adapter.input.api.v1.rag import rag_router as rag_v1_router

router = APIRouter()
router.include_router(rag_v1_router, prefix="/api/v1/rag", tags=["RAG"])


__all__ = ["router"]
