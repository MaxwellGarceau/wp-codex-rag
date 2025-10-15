"""
LLM-only handler for orchestrating LLM-only operations.
"""

from typing import Any

from app.rag.application.dto import RAGQueryRequestDTO, RAGQueryResponseDTO
from app.rag.application.service.llm_service import LLMService
from app.rag.application.service.llm_service_factory import LLMServiceFactory
from app.rag.application.service.prompt_service import PromptService
from core.logging_config import get_logger

logger = get_logger(__name__)


class LLMOnlyHandler:
    """Handler for LLM-only operations that orchestrates services."""

    def __init__(self, llm_service_factory: LLMServiceFactory) -> None:
        self.llm_service = LLMService(llm_service_factory)
        self.prompt_service = PromptService()

    async def handle_query(self, request: RAGQueryRequestDTO) -> dict[str, Any]:
        """
        Handle LLM-only query by orchestrating services.

        Args:
            request: The query request

        Returns:
            Dictionary containing the answer and empty sources
        """
        logger.info(
            f"Starting LLM-only query for question: {request.question[:100]}..."
        )

        try:
            # Build prompts without context
            system_prompt = self.prompt_service.get_llm_only_system_prompt()
            user_prompt = self.prompt_service.build_llm_only_user_prompt(
                request.question
            )

            logger.info(f"Final prompt length: {len(user_prompt)} characters")
            logger.debug(f"Final assembled prompt:\n{user_prompt}")

            # Generate answer using LLM without context
            logger.debug("Generating answer using LLM without context")
            answer = self.llm_service.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=150,
            )

            logger.info(f"Generated answer with {len(answer)} characters")
            logger.info("LLM-only query completed successfully")

            # Return empty sources since this is LLM-only
            response = RAGQueryResponseDTO(answer=answer, sources=[])
            return response.model_dump()

        except Exception as e:
            logger.error(f"Unexpected error in LLM-only query: {e!s}", exc_info=True)
            raise
