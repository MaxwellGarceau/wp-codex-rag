"""
Tests for LLMOnlyHandler.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.rag.application.dto import RAGQueryRequestDTO
from app.rag.application.handler.llm_only_handler import LLMOnlyHandler
from app.rag.application.service.llm_service_factory import LLMServiceFactory


class TestLLMOnlyHandler:
    """Test cases for LLMOnlyHandler."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_llm_factory = MagicMock(spec=LLMServiceFactory)
        self.handler = LLMOnlyHandler(self.mock_llm_factory)

    @pytest.mark.asyncio
    async def test_handle_query_successful(self) -> None:
        """Test successful LLM-only query handling."""
        # Arrange
        request = RAGQueryRequestDTO(question="How do I create a WordPress plugin?")
        expected_answer = "To create a WordPress plugin, you need to create a PHP file with a plugin header."

        # Mock the LLM service
        with patch.object(
            self.handler.llm_service,
            "generate_completion",
            return_value=expected_answer,
        ):
            # Act
            result = await self.handler.handle_query(request)

            # Assert
            assert result["answer"] == expected_answer
            assert result["sources"] == []  # Should be empty for LLM-only

            # Verify service call
            self.handler.llm_service.generate_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_query_completion_failure(self) -> None:
        """Test LLM-only query handling when completion generation fails."""
        # Arrange
        request = RAGQueryRequestDTO(question="How do I create a WordPress plugin?")

        # Mock completion generation to fail
        with patch.object(
            self.handler.llm_service,
            "generate_completion",
            side_effect=Exception("Completion generation failed"),
        ):
            # Act & Assert
            with pytest.raises(Exception, match="Completion generation failed"):
                await self.handler.handle_query(request)

    @pytest.mark.asyncio
    async def test_handle_query_prompt_usage(self) -> None:
        """Test that the handler uses the correct prompts."""
        # Arrange
        request = RAGQueryRequestDTO(question="How do I create a WordPress plugin?")
        expected_answer = "Test answer"

        # Mock the LLM service
        with patch.object(
            self.handler.llm_service,
            "generate_completion",
            return_value=expected_answer,
        ) as mock_completion:
            # Act
            await self.handler.handle_query(request)

            # Assert
            completion_call = mock_completion.call_args
            system_prompt = completion_call[1]["system_prompt"]
            user_prompt = completion_call[1]["user_prompt"]

            # Check that LLM-only system prompt is used
            assert "WordPress development" in system_prompt
            assert "plugin creation" in system_prompt
            assert "theme development" in system_prompt

            # Check that user prompt is simple (no context)
            assert user_prompt == f"Question: {request.question}"

    @pytest.mark.asyncio
    async def test_handle_query_parameters(self) -> None:
        """Test that the handler passes correct parameters to LLM service."""
        # Arrange
        request = RAGQueryRequestDTO(question="How do I create a WordPress plugin?")
        expected_answer = "Test answer"

        # Mock the LLM service
        with patch.object(
            self.handler.llm_service,
            "generate_completion",
            return_value=expected_answer,
        ) as mock_completion:
            # Act
            await self.handler.handle_query(request)

            # Assert
            completion_call = mock_completion.call_args
            assert completion_call[1]["temperature"] == 0.1
            assert completion_call[1]["max_tokens"] == 150

    @pytest.mark.asyncio
    async def test_handle_query_empty_sources(self) -> None:
        """Test that LLM-only handler always returns empty sources."""
        # Arrange
        request = RAGQueryRequestDTO(question="How do I create a WordPress plugin?")
        expected_answer = "Test answer"

        # Mock the LLM service
        with patch.object(
            self.handler.llm_service,
            "generate_completion",
            return_value=expected_answer,
        ):
            # Act
            result = await self.handler.handle_query(request)

            # Assert
            assert result["sources"] == []
            assert len(result["sources"]) == 0
