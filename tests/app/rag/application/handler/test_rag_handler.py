"""
Tests for RAGHandler.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.rag.application.dto import RAGQueryRequestDTO, RAGSourceDTO
from app.rag.application.handler.rag_handler import RAGHandler
from app.rag.application.service.llm_service_factory import LLMServiceFactory


class TestRAGHandler:
    """Test cases for RAGHandler."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_llm_factory = MagicMock(spec=LLMServiceFactory)
        self.handler = RAGHandler(self.mock_llm_factory)

    @pytest.mark.asyncio
    async def test_handle_query_successful(self) -> None:
        """Test successful RAG query handling."""
        # Arrange
        request = RAGQueryRequestDTO(question="How do I create a WordPress plugin?")
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        expected_answer = "To create a WordPress plugin, you need to create a PHP file with a plugin header."
        expected_contexts = ["Document 1 content", "Document 2 content"]
        expected_sources = [
            RAGSourceDTO(
                title="Plugin Development", url="https://example.com/plugin-dev"
            ),
            RAGSourceDTO(title="WordPress Basics", url="https://example.com/wp-basics"),
        ]

        # Mock the services
        with patch.object(
            self.handler.llm_service,
            "generate_embedding",
            return_value=expected_embedding,
        ), patch.object(
            self.handler.rag_service,
            "query_vector_db",
            return_value=(expected_contexts, expected_sources),
        ), patch.object(
            self.handler.llm_service,
            "generate_completion",
            return_value=expected_answer,
        ):
            # Act
            result = await self.handler.handle_query(request)

            # Assert
            assert result["answer"] == expected_answer
            assert len(result["sources"]) == 2
            assert result["sources"][0]["title"] == "Plugin Development"
            assert result["sources"][0]["url"] == "https://example.com/plugin-dev"
            assert result["sources"][1]["title"] == "WordPress Basics"
            assert result["sources"][1]["url"] == "https://example.com/wp-basics"

            # Verify service calls
            self.handler.llm_service.generate_embedding.assert_called_once_with(
                request.question
            )
            self.handler.rag_service.query_vector_db.assert_called_once_with(
                expected_embedding
            )
            self.handler.llm_service.generate_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_query_embedding_failure(self) -> None:
        """Test RAG query handling when embedding generation fails."""
        # Arrange
        request = RAGQueryRequestDTO(question="How do I create a WordPress plugin?")

        # Mock embedding generation to fail
        with patch.object(
            self.handler.llm_service,
            "generate_embedding",
            side_effect=Exception("Embedding generation failed"),
        ):
            # Act & Assert
            with pytest.raises(Exception, match="Embedding generation failed"):
                await self.handler.handle_query(request)

    @pytest.mark.asyncio
    async def test_handle_query_rag_failure(self) -> None:
        """Test RAG query handling when vector DB query fails."""
        # Arrange
        request = RAGQueryRequestDTO(question="How do I create a WordPress plugin?")
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        # Mock embedding generation to succeed but RAG query to fail
        with patch.object(
            self.handler.llm_service,
            "generate_embedding",
            return_value=expected_embedding,
        ), patch.object(
            self.handler.rag_service,
            "query_vector_db",
            side_effect=Exception("Vector DB query failed"),
        ):
            # Act & Assert
            with pytest.raises(Exception, match="Vector DB query failed"):
                await self.handler.handle_query(request)

    @pytest.mark.asyncio
    async def test_handle_query_completion_failure(self) -> None:
        """Test RAG query handling when completion generation fails."""
        # Arrange
        request = RAGQueryRequestDTO(question="How do I create a WordPress plugin?")
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        expected_contexts = ["Document 1 content"]
        expected_sources = [RAGSourceDTO(title="Test", url="https://example.com")]

        # Mock services to succeed until completion
        with patch.object(
            self.handler.llm_service,
            "generate_embedding",
            return_value=expected_embedding,
        ), patch.object(
            self.handler.rag_service,
            "query_vector_db",
            return_value=(expected_contexts, expected_sources),
        ), patch.object(
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
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        expected_contexts = ["Document 1 content"]
        expected_sources = [RAGSourceDTO(title="Test", url="https://example.com")]
        expected_answer = "Test answer"

        # Mock services
        with patch.object(
            self.handler.llm_service,
            "generate_embedding",
            return_value=expected_embedding,
        ), patch.object(
            self.handler.rag_service,
            "query_vector_db",
            return_value=(expected_contexts, expected_sources),
        ), patch.object(
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

            # Check that RAG system prompt is used
            assert "provided context" in system_prompt
            assert "SHORT and FOCUSED" in system_prompt

            # Check that user prompt includes context
            assert request.question in user_prompt
            assert "Context:" in user_prompt
            assert "Document 1 content" in user_prompt
