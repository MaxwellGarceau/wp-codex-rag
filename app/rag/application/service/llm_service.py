"""
Dedicated LLM service for pure LLM operations.
"""


from app.rag.application.service.llm_service_factory import LLMServiceFactory
from app.rag.domain.enum.llm_operation import LLMOperation
from app.rag.domain.enum.llm_provider import LLMProvider
from core.logging_config import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for pure LLM operations - embeddings and completions."""

    def __init__(self, llm_service_factory: LLMServiceFactory) -> None:
        self.llm_factory = llm_service_factory

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embeddings for the given text.

        Args:
            text: The text to generate embeddings for

        Returns:
            List of embedding values
        """
        logger.debug("Generating embeddings for text")
        return self.llm_factory.execute_operation(
            operation=LLMOperation.EMBEDDING,
            provider=LLMProvider.GROQ,
            text=text,
        )

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 150,
    ) -> str:
        """
        Generate a completion using the LLM.

        Args:
            system_prompt: The system prompt to set context
            user_prompt: The user prompt with the question/request
            temperature: Temperature for response generation
            max_tokens: Maximum tokens for the response

        Returns:
            The generated completion text
        """
        logger.debug("Generating completion using LLM")
        return self.llm_factory.execute_operation(
            operation=LLMOperation.COMPLETION,
            provider=LLMProvider.GROQ,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
