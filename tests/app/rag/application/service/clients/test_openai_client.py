"""
Unit tests for OpenAIClient class.

This module contains comprehensive tests for the OpenAIClient class,
covering embedding generation, completion generation, error handling,
and integration with OpenAI API.
"""

from unittest.mock import Mock

import pytest
from openai import APIError, RateLimitError

from app.rag.application.service.clients.openai_client import OpenAIClient


class TestOpenAIClient:
    """Test cases for OpenAIClient class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_openai_client = Mock()
        self.client = OpenAIClient(self.mock_openai_client)

    def test_init(self) -> None:
        """Test OpenAIClient initialization."""
        assert self.client.client == self.mock_openai_client

    def test_generate_embedding_success(self) -> None:
        """Test successful embedding generation."""
        # Arrange
        text = "Test text for embedding"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        # Mock OpenAI client response
        mock_embedding_data = Mock()
        mock_embedding_data.embedding = expected_embedding
        mock_embeddings_response = Mock()
        mock_embeddings_response.data = [mock_embedding_data]
        self.mock_openai_client.embeddings.create.return_value = (
            mock_embeddings_response
        )

        # Act
        result = self.client.generate_embedding(text)

        # Assert
        assert result == expected_embedding
        self.mock_openai_client.embeddings.create.assert_called_once_with(
            input=[text],
            model="text-embedding-3-small",  # Default model from config
        )

    def test_generate_embedding_rate_limit_error(self) -> None:
        """Test embedding generation with rate limit error."""
        # Arrange
        text = "Test text for embedding"
        self.mock_openai_client.embeddings.create.side_effect = RateLimitError(
            "Rate limit exceeded", response=Mock(), body={}
        )

        # Act & Assert
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            self.client.generate_embedding(text)

    def test_generate_embedding_api_error(self) -> None:
        """Test embedding generation with API error."""
        # Arrange
        text = "Test text for embedding"
        self.mock_openai_client.embeddings.create.side_effect = APIError(
            "API error", response=Mock(), body={}
        )

        # Act & Assert
        with pytest.raises(APIError, match="API error"):
            self.client.generate_embedding(text)

    def test_generate_completion_success(self) -> None:
        """Test successful completion generation."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        expected_completion = "WordPress is a content management system."

        # Mock OpenAI client response
        mock_choice = Mock()
        mock_choice.message.content = expected_completion
        mock_choice.finish_reason = "stop"
        mock_completion_response = Mock()
        mock_completion_response.choices = [mock_choice]
        self.mock_openai_client.chat.completions.create.return_value = (
            mock_completion_response
        )

        # Act
        result = self.client.generate_completion(system_prompt, user_prompt)

        # Assert
        assert result == expected_completion
        self.mock_openai_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o-mini",  # Default model from config
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

    def test_generate_completion_with_max_tokens(self) -> None:
        """Test completion generation with max_tokens parameter."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        max_tokens = 100
        expected_completion = "WordPress is a content management system."

        # Mock OpenAI client response
        mock_choice = Mock()
        mock_choice.message.content = expected_completion
        mock_choice.finish_reason = "stop"
        mock_completion_response = Mock()
        mock_completion_response.choices = [mock_choice]
        self.mock_openai_client.chat.completions.create.return_value = (
            mock_completion_response
        )

        # Act
        result = self.client.generate_completion(
            system_prompt, user_prompt, temperature=0.5, max_tokens=max_tokens
        )

        # Assert
        assert result == expected_completion
        self.mock_openai_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=max_tokens,
        )

    def test_generate_completion_without_max_tokens(self) -> None:
        """Test completion generation without max_tokens parameter."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        expected_completion = "WordPress is a content management system."

        # Mock OpenAI client response
        mock_choice = Mock()
        mock_choice.message.content = expected_completion
        mock_choice.finish_reason = "stop"
        mock_completion_response = Mock()
        mock_completion_response.choices = [mock_choice]
        self.mock_openai_client.chat.completions.create.return_value = (
            mock_completion_response
        )

        # Act
        result = self.client.generate_completion(
            system_prompt, user_prompt, max_tokens=None
        )

        # Assert
        assert result == expected_completion
        call_args = self.mock_openai_client.chat.completions.create.call_args[1]
        assert "max_tokens" not in call_args

    def test_generate_completion_with_custom_temperature(self) -> None:
        """Test completion generation with custom temperature."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        temperature = 0.8
        expected_completion = "WordPress is a content management system."

        # Mock OpenAI client response
        mock_choice = Mock()
        mock_choice.message.content = expected_completion
        mock_choice.finish_reason = "stop"
        mock_completion_response = Mock()
        mock_completion_response.choices = [mock_choice]
        self.mock_openai_client.chat.completions.create.return_value = (
            mock_completion_response
        )

        # Act
        result = self.client.generate_completion(
            system_prompt, user_prompt, temperature=temperature
        )

        # Assert
        assert result == expected_completion
        self.mock_openai_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )

    def test_generate_completion_rate_limit_error(self) -> None:
        """Test completion generation with rate limit error."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        self.mock_openai_client.chat.completions.create.side_effect = RateLimitError(
            "Rate limit exceeded", response=Mock(), body={}
        )

        # Act & Assert
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            self.client.generate_completion(system_prompt, user_prompt)

    def test_generate_completion_api_error(self) -> None:
        """Test completion generation with API error."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        self.mock_openai_client.chat.completions.create.side_effect = APIError(
            "API error", response=Mock(), body={}
        )

        # Act & Assert
        with pytest.raises(APIError, match="API error"):
            self.client.generate_completion(system_prompt, user_prompt)

    def test_generate_completion_empty_content(self) -> None:
        """Test completion generation with empty content response."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"

        # Mock OpenAI client response with None content
        mock_choice = Mock()
        mock_choice.message.content = None
        mock_choice.finish_reason = "stop"
        mock_completion_response = Mock()
        mock_completion_response.choices = [mock_choice]
        self.mock_openai_client.chat.completions.create.return_value = (
            mock_completion_response
        )

        # Act
        result = self.client.generate_completion(system_prompt, user_prompt)

        # Assert
        assert result == ""

    def test_handle_token_limit_truncation_length_finish_reason(self) -> None:
        """Test token limit truncation handling with length finish reason."""
        # Arrange
        answer = "This is a partial answer that was truncated"
        max_tokens = 100

        # Mock completion response
        mock_choice = Mock()
        mock_choice.finish_reason = "length"
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]

        # Act
        result = self.client._handle_token_limit_truncation(
            answer, mock_completion, max_tokens
        )

        # Assert
        expected = answer + "\n\n[Response truncated due to length limit]"
        assert result == expected

    def test_handle_token_limit_truncation_stop_finish_reason(self) -> None:
        """Test token limit truncation handling with stop finish reason."""
        # Arrange
        answer = "This is a complete answer"
        max_tokens = 100

        # Mock completion response
        mock_choice = Mock()
        mock_choice.finish_reason = "stop"
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]

        # Act
        result = self.client._handle_token_limit_truncation(
            answer, mock_completion, max_tokens
        )

        # Assert
        assert result == answer  # No truncation message added

    def test_handle_token_limit_truncation_none_finish_reason(self) -> None:
        """Test token limit truncation handling with None finish reason."""
        # Arrange
        answer = "This is an answer with no finish reason"
        max_tokens = 100

        # Mock completion response
        mock_choice = Mock()
        mock_choice.finish_reason = None
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]

        # Act
        result = self.client._handle_token_limit_truncation(
            answer, mock_completion, max_tokens
        )

        # Assert
        assert result == answer  # No truncation message added

    def test_handle_token_limit_truncation_none_max_tokens(self) -> None:
        """Test token limit truncation handling with None max_tokens."""
        # Arrange
        answer = "This is an answer with no max tokens limit"
        max_tokens = None

        # Mock completion response
        mock_choice = Mock()
        mock_choice.finish_reason = "length"
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]

        # Act
        result = self.client._handle_token_limit_truncation(
            answer, mock_completion, max_tokens
        )

        # Assert
        assert result == answer  # No truncation message added when max_tokens is None
