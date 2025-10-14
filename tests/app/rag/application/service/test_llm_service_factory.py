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
        self.mock_huggingface_client = Mock(spec=LLMClientInterface)
        self.mock_huggingface_client = Mock(spec=LLMClientInterface)
        self.factory = LLMServiceFactory(
            {
                LLMProvider.HUGGINGFACE: self.mock_huggingface_client,
            }
        )

    def test_init(self):
        """Test LLMServiceFactory initialization."""
        mock_client = Mock(spec=LLMClientInterface)
        factory = LLMServiceFactory({LLMProvider.HUGGINGFACE: mock_client})
        assert LLMProvider.HUGGINGFACE in factory.clients
        assert factory.clients[LLMProvider.HUGGINGFACE] == mock_client

    def test_init_with_single_client(self):
        """Test LLMServiceFactory initialization with single client."""
        mock_huggingface_client = Mock(spec=LLMClientInterface)
        factory = LLMServiceFactory(
            {
                LLMProvider.HUGGINGFACE: mock_huggingface_client,
            }
        )

        assert LLMProvider.HUGGINGFACE in factory.clients
        assert factory.clients[LLMProvider.HUGGINGFACE] == mock_huggingface_client

    def test_execute_embedding_operation(self):
        """Test executing embedding operation."""
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        self.mock_huggingface_client.generate_embedding.return_value = expected_embedding

        result = self.factory.execute_operation(
            operation=LLMOperation.EMBEDDING,
            provider=LLMProvider.HUGGINGFACE,
            text="test text",
        )

        assert result == expected_embedding
        self.mock_huggingface_client.generate_embedding.assert_called_once_with("test text")

    def test_execute_embedding_operation_with_huggingface(self):
        """Test executing embedding operation with HuggingFace provider."""
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        self.mock_huggingface_client.generate_embedding.return_value = (
            expected_embedding
        )

        result = self.factory.execute_operation(
            operation=LLMOperation.EMBEDDING,
            provider=LLMProvider.HUGGINGFACE,
            text="test text",
        )

        assert result == expected_embedding
        self.mock_huggingface_client.generate_embedding.assert_called_once_with(
            "test text"
        )

    def test_execute_completion_operation(self):
        """Test executing completion operation."""
        expected_completion = "Generated answer"
        self.mock_huggingface_client.generate_completion.return_value = expected_completion

        result = self.factory.execute_operation(
            operation=LLMOperation.COMPLETION,
            provider=LLMProvider.HUGGINGFACE,
            system_prompt="You are a helpful assistant",
            user_prompt="Test question",
            temperature=0.2,
        )

        assert result == expected_completion
        self.mock_huggingface_client.generate_completion.assert_called_once_with(
            "You are a helpful assistant", "Test question", 0.2, None
        )

    def test_execute_completion_operation_with_max_tokens(self):
        """Test executing completion operation with max_tokens parameter."""
        expected_completion = "Generated answer"
        self.mock_huggingface_client.generate_completion.return_value = expected_completion

        result = self.factory.execute_operation(
            operation=LLMOperation.COMPLETION,
            provider=LLMProvider.HUGGINGFACE,
            system_prompt="You are a helpful assistant",
            user_prompt="Test question",
            temperature=0.5,
            max_tokens=100,
        )

        assert result == expected_completion
        self.mock_huggingface_client.generate_completion.assert_called_once_with(
            "You are a helpful assistant", "Test question", 0.5, 100
        )

    def test_execute_completion_operation_with_none_max_tokens(self):
        """Test executing completion operation with None max_tokens."""
        expected_completion = "Generated answer"
        self.mock_huggingface_client.generate_completion.return_value = expected_completion

        result = self.factory.execute_operation(
            operation=LLMOperation.COMPLETION,
            provider=LLMProvider.HUGGINGFACE,
            system_prompt="You are a helpful assistant",
            user_prompt="Test question",
            temperature=0.2,
            max_tokens=None,
        )

        assert result == expected_completion
        self.mock_huggingface_client.generate_completion.assert_called_once_with(
            "You are a helpful assistant", "Test question", 0.2, None
        )

    def test_execute_completion_operation_with_huggingface(self):
        """Test executing completion operation with HuggingFace provider."""
        expected_completion = "Generated answer from HuggingFace"
        self.mock_huggingface_client.generate_completion.return_value = (
            expected_completion
        )

        result = self.factory.execute_operation(
            operation=LLMOperation.COMPLETION,
            provider=LLMProvider.HUGGINGFACE,
            system_prompt="You are a helpful assistant",
            user_prompt="Test question",
            temperature=0.1,
            max_tokens=150,
        )

        assert result == expected_completion
        self.mock_huggingface_client.generate_completion.assert_called_once_with(
            "You are a helpful assistant", "Test question", 0.1, 150
        )

    def test_execute_completion_operation_with_extra_kwargs(self):
        """Test executing completion operation with extra kwargs."""
        expected_completion = "Generated answer"
        self.mock_huggingface_client.generate_completion.return_value = expected_completion

        result = self.factory.execute_operation(
            operation=LLMOperation.COMPLETION,
            provider=LLMProvider.HUGGINGFACE,
            system_prompt="You are a helpful assistant",
            user_prompt="Test question",
            temperature=0.2,
            max_tokens=100,
            extra_param="ignored",
        )

        assert result == expected_completion
        # Extra kwargs should be ignored
        self.mock_huggingface_client.generate_completion.assert_called_once_with(
            "You are a helpful assistant", "Test question", 0.2, 100
        )

    def test_execute_operation_with_unsupported_operation(self):
        """Test executing unsupported operation raises error."""
        with pytest.raises(ValueError, match="Unsupported operation"):
            self.factory.execute_operation(
                operation="unsupported_operation",  # type: ignore
                provider=LLMProvider.HUGGINGFACE,
            )

    def test_execute_operation_with_unsupported_provider(self):
        """Test executing operation with unsupported provider raises error."""
        with pytest.raises(ValueError, match="No client available for provider"):
            self.factory.execute_operation(
                operation=LLMOperation.EMBEDDING,
                provider="unsupported_provider",  # type: ignore
            )

    def test_execute_operation_with_none_provider(self):
        """Test executing operation with None provider raises error."""
        with pytest.raises(ValueError, match="No client available for provider"):
            self.factory.execute_operation(
                operation=LLMOperation.EMBEDDING,
                provider=None,  # type: ignore
            )

    def test_execute_operation_with_none_operation(self):
        """Test executing operation with None operation raises error."""
        with pytest.raises(ValueError, match="Unsupported operation"):
            self.factory.execute_operation(
                operation=None,  # type: ignore
                provider=LLMProvider.HUGGINGFACE,
            )

    def test_get_client(self):
        """Test getting client for supported provider."""
        client = self.factory._get_client(LLMProvider.HUGGINGFACE)
        assert client == self.mock_huggingface_client

    def test_get_client_huggingface(self):
        """Test getting client for HuggingFace provider."""
        client = self.factory._get_client(LLMProvider.HUGGINGFACE)
        assert client == self.mock_huggingface_client

    def test_get_client_unsupported_provider(self):
        """Test getting client for unsupported provider raises error."""
        with pytest.raises(ValueError, match="No client available for provider"):
            self.factory._get_client("unsupported_provider")  # type: ignore

    def test_get_client_none_provider(self):
        """Test getting client for None provider raises error."""
        with pytest.raises(ValueError, match="No client available for provider"):
            self.factory._get_client(None)  # type: ignore

    def test_handle_embedding_with_extra_kwargs(self):
        """Test embedding handler ignores extra kwargs."""
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        self.mock_huggingface_client.generate_embedding.return_value = expected_embedding

        result = self.factory._handle_embedding(
            self.mock_huggingface_client, text="test text", extra_param="ignored"
        )

        assert result == expected_embedding
        self.mock_huggingface_client.generate_embedding.assert_called_once_with("test text")

    def test_handle_completion_with_extra_kwargs(self):
        """Test completion handler ignores extra kwargs."""
        expected_completion = "Generated answer"
        self.mock_huggingface_client.generate_completion.return_value = expected_completion

        result = self.factory._handle_completion(
            self.mock_huggingface_client,
            system_prompt="You are a helpful assistant",
            user_prompt="Test question",
            temperature=0.2,
            max_tokens=100,
            extra_param="ignored",
        )

        assert result == expected_completion
        self.mock_huggingface_client.generate_completion.assert_called_once_with(
            "You are a helpful assistant", "Test question", 0.2, 100
        )

    def test_operation_handlers_mapping(self):
        """Test that operation handlers are properly mapped."""
        assert LLMOperation.EMBEDDING in self.factory._operation_handlers
        assert LLMOperation.COMPLETION in self.factory._operation_handlers
        assert (
            self.factory._operation_handlers[LLMOperation.EMBEDDING]
            == self.factory._handle_embedding
        )
        assert (
            self.factory._operation_handlers[LLMOperation.COMPLETION]
            == self.factory._handle_completion
        )

    def test_empty_clients_dict(self):
        """Test factory initialization with empty clients dictionary."""
        factory = LLMServiceFactory({})
        assert factory.clients == {}

    def test_execute_operation_with_empty_clients(self):
        """Test executing operation with empty clients dictionary."""
        factory = LLMServiceFactory({})

        with pytest.raises(ValueError, match="No client available for provider"):
            factory.execute_operation(
                operation=LLMOperation.EMBEDDING,
                provider=LLMProvider.HUGGINGFACE,
                text="test",
            )
