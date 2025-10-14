"""
Unit tests for GroqClient class.

This module contains comprehensive tests for the GroqClient class,
covering embedding generation, completion generation, error handling,
and integration with Groq API and HuggingFace embedding models.
"""

from unittest.mock import Mock, patch

import pytest

from app.rag.application.service.clients.groq_client import GroqClient


class TestGroqClient:
    """Test cases for GroqClient class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        with patch(
            "app.rag.application.service.clients.groq_client.SentenceTransformer"
        ), patch("app.rag.application.service.clients.groq_client.Groq"), patch(
            "app.rag.application.service.clients.groq_client.config"
        ) as mock_config:
            mock_config.GROQ_API_KEY = "test-api-key"
            self.client = GroqClient()

    def test_init(self) -> None:
        """Test GroqClient initialization."""
        assert hasattr(self.client, "embedding_model")
        assert hasattr(self.client, "groq_client")
        assert hasattr(self.client, "completion_model_name")
        assert self.client.completion_model_name == "llama-3.3-70b-versatile"

    def test_init_without_api_key(self) -> None:
        """Test GroqClient initialization without API key raises error."""
        with patch(
            "app.rag.application.service.clients.groq_client.SentenceTransformer"
        ), patch(
            "app.rag.application.service.clients.groq_client.config"
        ) as mock_config:
            mock_config.GROQ_API_KEY = ""

            with pytest.raises(
                ValueError, match="GROQ_API_KEY is required but not set"
            ):
                GroqClient()

    def test_generate_embedding_success(self) -> None:
        """Test successful embedding generation."""
        # Arrange
        text = "Test text for embedding"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        # Mock embedding model
        mock_embedding = Mock()
        mock_embedding.tolist.return_value = expected_embedding
        self.client.embedding_model.encode.return_value = mock_embedding

        # Act
        result = self.client.generate_embedding(text)

        # Assert
        assert result == expected_embedding
        self.client.embedding_model.encode.assert_called_once_with(
            text, convert_to_tensor=False
        )

    def test_generate_embedding_failure(self) -> None:
        """Test embedding generation failure."""
        # Arrange
        text = "Test text for embedding"
        self.client.embedding_model.encode.side_effect = Exception("Embedding failed")

        # Act & Assert
        with pytest.raises(Exception, match="Embedding failed"):
            self.client.generate_embedding(text)

    def test_generate_completion_success(self) -> None:
        """Test successful completion generation."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        expected_completion = "WordPress is a content management system."

        # Mock Groq API response
        mock_choice = Mock()
        mock_choice.message.content = expected_completion
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        self.client.groq_client.chat.completions.create.return_value = mock_response

        # Act
        result = self.client.generate_completion(system_prompt, user_prompt)

        # Assert
        assert result == expected_completion
        self.client.groq_client.chat.completions.create.assert_called_once()

        # Verify the call arguments
        call_args = self.client.groq_client.chat.completions.create.call_args[1]
        assert call_args["messages"] == [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        assert call_args["model"] == "llama-3.3-70b-versatile"
        assert call_args["temperature"] == 0.2
        assert call_args["stream"] is False

    def test_generate_completion_with_parameters(self) -> None:
        """Test completion generation with custom parameters."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        temperature = 0.8
        max_tokens = 200
        expected_completion = "WordPress is a content management system."

        # Mock Groq API response
        mock_choice = Mock()
        mock_choice.message.content = expected_completion
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        self.client.groq_client.chat.completions.create.return_value = mock_response

        # Act
        result = self.client.generate_completion(
            system_prompt,
            user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Assert
        assert result == expected_completion
        call_args = self.client.groq_client.chat.completions.create.call_args[1]
        assert call_args["temperature"] == temperature
        assert call_args["max_tokens"] == max_tokens

    def test_generate_completion_without_max_tokens(self) -> None:
        """Test completion generation without max_tokens parameter."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        expected_completion = "WordPress is a content management system."

        # Mock Groq API response
        mock_choice = Mock()
        mock_choice.message.content = expected_completion
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        self.client.groq_client.chat.completions.create.return_value = mock_response

        # Act
        result = self.client.generate_completion(
            system_prompt, user_prompt, max_tokens=None
        )

        # Assert
        assert result == expected_completion
        call_args = self.client.groq_client.chat.completions.create.call_args[1]
        assert "max_tokens" not in call_args

    def test_generate_completion_failure(self) -> None:
        """Test completion generation failure."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        self.client.groq_client.chat.completions.create.side_effect = Exception(
            "API failed"
        )

        # Act & Assert
        with pytest.raises(Exception, match="API failed"):
            self.client.generate_completion(system_prompt, user_prompt)

    def test_generate_completion_empty_response(self) -> None:
        """Test completion generation with empty response."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"

        # Mock Groq API response with empty content
        mock_choice = Mock()
        mock_choice.message.content = None
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        self.client.groq_client.chat.completions.create.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match="Empty response received from Groq API"):
            self.client.generate_completion(system_prompt, user_prompt)

    def test_generate_completion_messages_format(self) -> None:
        """Test that messages are properly formatted for Groq API."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        expected_completion = "WordPress is a CMS."

        # Mock Groq API response
        mock_choice = Mock()
        mock_choice.message.content = expected_completion
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        self.client.groq_client.chat.completions.create.return_value = mock_response

        # Act
        self.client.generate_completion(system_prompt, user_prompt)

        # Assert
        call_args = self.client.groq_client.chat.completions.create.call_args[1]
        expected_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        assert call_args["messages"] == expected_messages

    def test_generate_completion_default_parameters(self) -> None:
        """Test that default parameters are correctly set."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        expected_completion = "WordPress is a CMS."

        # Mock Groq API response
        mock_choice = Mock()
        mock_choice.message.content = expected_completion
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        self.client.groq_client.chat.completions.create.return_value = mock_response

        # Act
        self.client.generate_completion(system_prompt, user_prompt)

        # Assert
        call_args = self.client.groq_client.chat.completions.create.call_args[1]
        assert call_args["model"] == "llama-3.3-70b-versatile"
        assert call_args["temperature"] == 0.2
        assert call_args["stream"] is False
