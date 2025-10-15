"""
Tests for LLMService.
"""

from unittest.mock import MagicMock

from app.rag.application.service.llm_service import LLMService
from app.rag.application.service.llm_service_factory import LLMServiceFactory
from app.rag.domain.enum.llm_operation import LLMOperation
from app.rag.domain.enum.llm_provider import LLMProvider


class TestLLMService:
    """Test cases for LLMService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_llm_factory = MagicMock(spec=LLMServiceFactory)
        self.llm_service = LLMService(self.mock_llm_factory)

    def test_init(self) -> None:
        """Test LLMService initialization."""
        assert self.llm_service.llm_factory == self.mock_llm_factory

    def test_generate_embedding(self) -> None:
        """Test generate_embedding method."""
        # Arrange
        text = "Test text for embedding"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        self.mock_llm_factory.execute_operation.return_value = expected_embedding

        # Act
        result = self.llm_service.generate_embedding(text)

        # Assert
        assert result == expected_embedding
        self.mock_llm_factory.execute_operation.assert_called_once_with(
            operation=LLMOperation.EMBEDDING,
            provider=LLMProvider.GROQ,
            text=text,
        )

    def test_generate_completion_default_parameters(self) -> None:
        """Test generate_completion with default parameters."""
        # Arrange
        system_prompt = "You are a helpful assistant."
        user_prompt = "What is WordPress?"
        expected_answer = "WordPress is a content management system."
        self.mock_llm_factory.execute_operation.return_value = expected_answer

        # Act
        result = self.llm_service.generate_completion(system_prompt, user_prompt)

        # Assert
        assert result == expected_answer
        self.mock_llm_factory.execute_operation.assert_called_once_with(
            operation=LLMOperation.COMPLETION,
            provider=LLMProvider.GROQ,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=150,
        )

    def test_generate_completion_custom_parameters(self) -> None:
        """Test generate_completion with custom parameters."""
        # Arrange
        system_prompt = "You are a helpful assistant."
        user_prompt = "What is WordPress?"
        temperature = 0.5
        max_tokens = 200
        expected_answer = "WordPress is a content management system."
        self.mock_llm_factory.execute_operation.return_value = expected_answer

        # Act
        result = self.llm_service.generate_completion(
            system_prompt, user_prompt, temperature, max_tokens
        )

        # Assert
        assert result == expected_answer
        self.mock_llm_factory.execute_operation.assert_called_once_with(
            operation=LLMOperation.COMPLETION,
            provider=LLMProvider.GROQ,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
