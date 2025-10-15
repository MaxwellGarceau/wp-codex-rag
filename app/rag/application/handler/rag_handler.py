"""
RAG handler for orchestrating RAG operations.
"""

from typing import Any

from app.rag.application.dto import RAGQueryRequestDTO, RAGQueryResponseDTO
from app.rag.application.service.llm_service import LLMService
from app.rag.application.service.llm_service_factory import LLMServiceFactory
from app.rag.application.service.prompt_service import PromptService
from app.rag.application.service.rag import RAGService
from core.logging_config import get_logger

logger = get_logger(__name__)


class RAGHandler:
    """Handler for RAG operations that orchestrates services."""

    def __init__(self, llm_service_factory: LLMServiceFactory) -> None:
        self.llm_service = LLMService(llm_service_factory)
        self.rag_service = RAGService()
        self.prompt_service = PromptService()

    async def handle_query(self, request: RAGQueryRequestDTO) -> dict[str, Any]:
        """
        Handle RAG query by orchestrating services.

        Args:
            request: The RAG query request

        Returns:
            Dictionary containing the answer and sources
        """
        logger.info(f"Starting RAG query for question: {request.question[:100]}...")

        try:
            # Generate embedding for the question
            logger.debug("Generating embeddings for question")
            query_embedding = self.llm_service.generate_embedding(request.question)

            # Query vector database for relevant documents
            contexts, sources = self.rag_service.query_vector_db(query_embedding)

            # Build prompts with context
            system_prompt = self.prompt_service.get_rag_system_prompt()
            user_prompt = self.prompt_service.build_rag_user_prompt(
                request.question, contexts
            )

            logger.info(f"Final prompt length: {len(user_prompt)} characters")
            logger.debug(f"Final assembled prompt:\n{user_prompt}")

            # Generate answer using LLM with context
            logger.debug("Generating answer using LLM with RAG context")
            answer = self.llm_service.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=150,
            )

            logger.info(f"Generated answer with {len(answer)} characters")
            logger.info("RAG query completed successfully")

            response = RAGQueryResponseDTO(answer=answer, sources=sources)
            return response.model_dump()

        except Exception as e:
            logger.error(f"Unexpected error in RAG query: {e!s}", exc_info=True)
            raise
