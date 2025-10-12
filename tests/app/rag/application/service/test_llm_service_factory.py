from unittest.mock import Mock

import pytest

from app.rag.application.service.llm_service_factory import LLMServiceFactory
from app.rag.domain.enum.llm_operation import LLMOperation
from app.rag.domain.enum.llm_provider import LLMProvider
from app.rag.domain.interface.llm_client import LLMClientInterface


class TestLLMServiceFactory:
    """Test cases for LLMServiceFactory class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_client = Mock(spec=LLMClientInterface)
        self.factory = LLMServiceFactory({LLMProvider.OPENAI: self.mock_client})

    def test_init(self):
        """Test LLMServiceFactory initialization."""
        mock_client = Mock(spec=LLMClientInterface)
        factory = LLMServiceFactory({LLMProvider.OPENAI: mock_client})
        assert LLMProvider.OPENAI in factory.clients
        assert factory.clients[LLMProvider.OPENAI] == mock_client

    def test_execute_embedding_operation(self):
        """Test executing embedding operation."""
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        self.mock_client.generate_embedding.return_value = expected_embedding

        result = self.factory.execute_operation(
            operation=LLMOperation.EMBEDDING,
            provider=LLMProvider.OPENAI,
            text="test text",
        )

        assert result == expected_embedding
        self.mock_client.generate_embedding.assert_called_once_with("test text")

    def test_execute_completion_operation(self):
        """Test executing completion operation."""
        expected_completion = "Generated answer"
        self.mock_client.generate_completion.return_value = expected_completion

        result = self.factory.execute_operation(
            operation=LLMOperation.COMPLETION,
            provider=LLMProvider.OPENAI,
            system_prompt="You are a helpful assistant",
            user_prompt="Test question",
            temperature=0.2,
        )

        assert result == expected_completion
        self.mock_client.generate_completion.assert_called_once_with(
            "You are a helpful assistant", "Test question", 0.2
        )

    def test_execute_operation_with_unsupported_operation(self):
        """Test executing unsupported operation raises error."""
        with pytest.raises(ValueError, match="Unsupported operation"):
            self.factory.execute_operation(
                operation="unsupported_operation",  # type: ignore
                provider=LLMProvider.OPENAI,
            )

    def test_execute_operation_with_unsupported_provider(self):
        """Test executing operation with unsupported provider raises error."""
        with pytest.raises(ValueError, match="No client available for provider"):
            self.factory.execute_operation(
                operation=LLMOperation.EMBEDDING,
                provider="unsupported_provider",  # type: ignore
            )

    def test_get_client(self):
        """Test getting client for supported provider."""
        client = self.factory._get_client(LLMProvider.OPENAI)
        assert client == self.mock_client

    def test_get_client_unsupported_provider(self):
        """Test getting client for unsupported provider raises error."""
        with pytest.raises(ValueError, match="No client available for provider"):
            self.factory._get_client("unsupported_provider")  # type: ignore
