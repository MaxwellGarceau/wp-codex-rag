"""
Unit tests for RAGService class.

This module contains comprehensive tests for the RAGService class,
covering query operations, error handling, and integration with the LLM factory.
"""

from unittest.mock import Mock, patch

import pytest

from app.rag.application.service.llm_service_factory import LLMServiceFactory
from app.rag.application.service.rag import RAGService
from app.rag.domain.enum.llm_operation import LLMOperation
from app.rag.domain.enum.llm_provider import LLMProvider


class TestRAGService:
    """Test cases for RAGService class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_llm_factory = Mock(spec=LLMServiceFactory)
        self.mock_chroma_client = Mock()
        self.mock_collection = Mock()

        # Mock ChromaDB client and collection
        self.mock_chroma_client.get_or_create_collection.return_value = (
            self.mock_collection
        )

        with patch("app.rag.application.service.rag.chromadb") as mock_chromadb:
            mock_chromadb.HttpClient.return_value = self.mock_chroma_client
            self.rag_service = RAGService(self.mock_llm_factory)

    def test_init(self) -> None:
        """Test RAGService initialization."""
        assert self.rag_service.llm_factory == self.mock_llm_factory
        assert self.rag_service.client == self.mock_chroma_client
        assert self.rag_service.collection == self.mock_collection

    @pytest.mark.asyncio
    async def test_query_successful(self) -> None:
        """Test successful RAG query operation."""
        # Arrange
        question = "How do I create a WordPress plugin?"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        expected_answer = "To create a WordPress plugin, you need to create a PHP file with a plugin header."

        # Mock LLM factory responses
        self.mock_llm_factory.execute_operation.side_effect = [
            expected_embedding,  # First call for embedding
            expected_answer,  # Second call for completion
        ]

        # Mock ChromaDB query response
        mock_results = {
            "documents": [["Document 1 content", "Document 2 content"]],
            "metadatas": [
                [
                    {
                        "title": "Plugin Development",
                        "url": "https://example.com/plugin-dev",
                    },
                    {
                        "title": "WordPress Basics",
                        "url": "https://example.com/wp-basics",
                    },
                ]
            ],
            "distances": [[0.1, 0.2]],
        }
        self.mock_collection.query.return_value = mock_results

        # Act
        result = await self.rag_service.query(question=question)

        # Assert
        assert result["answer"] == expected_answer
        assert len(result["sources"]) == 2
        assert result["sources"][0]["title"] == "Plugin Development"
        assert result["sources"][0]["url"] == "https://example.com/plugin-dev"
        assert result["sources"][1]["title"] == "WordPress Basics"
        assert result["sources"][1]["url"] == "https://example.com/wp-basics"

        # Verify LLM factory calls
        assert self.mock_llm_factory.execute_operation.call_count == 2

        # Check embedding call
        embedding_call = self.mock_llm_factory.execute_operation.call_args_list[0]
        assert embedding_call[1]["operation"] == LLMOperation.EMBEDDING
        assert embedding_call[1]["provider"] == LLMProvider.HUGGINGFACE
        assert embedding_call[1]["text"] == question

        # Check completion call
        completion_call = self.mock_llm_factory.execute_operation.call_args_list[1]
        assert completion_call[1]["operation"] == LLMOperation.COMPLETION
        assert completion_call[1]["provider"] == LLMProvider.HUGGINGFACE
        assert completion_call[1]["temperature"] == 0.1
        assert completion_call[1]["max_tokens"] == 150
        assert (
            "Question: How do I create a WordPress plugin?"
            in completion_call[1]["user_prompt"]
        )

        # Verify ChromaDB query
        self.mock_collection.query.assert_called_once_with(
            query_embeddings=[expected_embedding],
            n_results=5,
            include=["metadatas", "documents", "distances"],
        )

    @pytest.mark.asyncio
    async def test_query_no_documents_found(self) -> None:
        """Test RAG query when no documents are found."""
        # Arrange
        question = "How do I create a WordPress plugin?"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        expected_answer = "I don't have enough information in the provided context."

        # Mock LLM factory responses
        self.mock_llm_factory.execute_operation.side_effect = [
            expected_embedding,  # First call for embedding
            expected_answer,  # Second call for completion
        ]

        # Mock ChromaDB query response with no documents
        mock_results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        self.mock_collection.query.return_value = mock_results

        # Act
        result = await self.rag_service.query(question=question)

        # Assert
        assert result["answer"] == expected_answer
        assert result["sources"] == []

        # Verify completion call with empty context
        completion_call = self.mock_llm_factory.execute_operation.call_args_list[1]
        assert "Context:\n" in completion_call[1]["user_prompt"]
        assert completion_call[1]["user_prompt"].endswith("Context:\n")

    @pytest.mark.asyncio
    async def test_query_with_missing_metadata(self) -> None:
        """Test RAG query with documents that have missing metadata."""
        # Arrange
        question = "How do I create a WordPress plugin?"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        expected_answer = "To create a WordPress plugin, you need to create a PHP file."

        # Mock LLM factory responses
        self.mock_llm_factory.execute_operation.side_effect = [
            expected_embedding,  # First call for embedding
            expected_answer,  # Second call for completion
        ]

        # Mock ChromaDB query response with missing metadata
        mock_results = {
            "documents": [["Document 1 content", "Document 2 content"]],
            "metadatas": [
                [
                    {"title": "Plugin Development"},  # Missing URL
                    {"url": "https://example.com/wp-basics"},  # Missing title
                ]
            ],
            "distances": [[0.1, 0.2]],
        }
        self.mock_collection.query.return_value = mock_results

        # Act
        result = await self.rag_service.query(question=question)

        # Assert
        assert result["answer"] == expected_answer
        assert len(result["sources"]) == 2
        assert result["sources"][0]["title"] == "Plugin Development"
        assert result["sources"][0]["url"] == ""  # Default empty string
        assert result["sources"][1]["title"] == "WordPress Codex"  # Default title
        assert result["sources"][1]["url"] == "https://example.com/wp-basics"

    @pytest.mark.asyncio
    async def test_query_embedding_generation_failure(self) -> None:
        """Test RAG query when embedding generation fails."""
        # Arrange
        question = "How do I create a WordPress plugin?"

        # Mock LLM factory to raise exception on embedding generation
        self.mock_llm_factory.execute_operation.side_effect = Exception(
            "Embedding generation failed"
        )

        # Act & Assert
        with pytest.raises(Exception, match="Embedding generation failed"):
            await self.rag_service.query(question=question)

    @pytest.mark.asyncio
    async def test_query_completion_generation_failure(self) -> None:
        """Test RAG query when completion generation fails."""
        # Arrange
        question = "How do I create a WordPress plugin?"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        # Mock LLM factory responses
        self.mock_llm_factory.execute_operation.side_effect = [
            expected_embedding,  # First call for embedding succeeds
            Exception("Completion generation failed"),  # Second call fails
        ]

        # Mock ChromaDB query response
        mock_results = {
            "documents": [["Document 1 content"]],
            "metadatas": [
                [{"title": "Plugin Development", "url": "https://example.com"}]
            ],
            "distances": [[0.1]],
        }
        self.mock_collection.query.return_value = mock_results

        # Act & Assert
        with pytest.raises(Exception, match="Completion generation failed"):
            await self.rag_service.query(question=question)

    @pytest.mark.asyncio
    async def test_query_chromadb_failure(self) -> None:
        """Test RAG query when ChromaDB query fails."""
        # Arrange
        question = "How do I create a WordPress plugin?"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        # Mock LLM factory embedding response
        self.mock_llm_factory.execute_operation.return_value = expected_embedding

        # Mock ChromaDB to raise exception
        self.mock_collection.query.side_effect = Exception("ChromaDB connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="ChromaDB connection failed"):
            await self.rag_service.query(question=question)

    @pytest.mark.asyncio
    async def test_query_system_prompt_content(self) -> None:
        """Test that the system prompt contains expected instructions."""
        # Arrange
        question = "How do I create a WordPress plugin?"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        expected_answer = "To create a WordPress plugin, you need to create a PHP file."

        # Mock LLM factory responses
        self.mock_llm_factory.execute_operation.side_effect = [
            expected_embedding,  # First call for embedding
            expected_answer,  # Second call for completion
        ]

        # Mock ChromaDB query response
        mock_results = {
            "documents": [["Document 1 content"]],
            "metadatas": [
                [{"title": "Plugin Development", "url": "https://example.com"}]
            ],
            "distances": [[0.1]],
        }
        self.mock_collection.query.return_value = mock_results

        # Act
        await self.rag_service.query(question=question)

        # Assert - Check system prompt content
        completion_call = self.mock_llm_factory.execute_operation.call_args_list[1]
        system_prompt = completion_call[1]["system_prompt"]

        assert "WordPress expert assistant" in system_prompt
        assert "SHORT and FOCUSED" in system_prompt
        assert "2-3 sentences maximum" in system_prompt
        assert "don't have enough information" in system_prompt

    @pytest.mark.asyncio
    async def test_query_user_prompt_structure(self) -> None:
        """Test that the user prompt is properly structured."""
        # Arrange
        question = "How do I create a WordPress plugin?"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        expected_answer = "To create a WordPress plugin, you need to create a PHP file."

        # Mock LLM factory responses
        self.mock_llm_factory.execute_operation.side_effect = [
            expected_embedding,  # First call for embedding
            expected_answer,  # Second call for completion
        ]

        # Mock ChromaDB query response
        mock_results = {
            "documents": [["Document 1 content", "Document 2 content"]],
            "metadatas": [
                [
                    {
                        "title": "Plugin Development",
                        "url": "https://example.com/plugin-dev",
                    },
                    {
                        "title": "WordPress Basics",
                        "url": "https://example.com/wp-basics",
                    },
                ]
            ],
            "distances": [[0.1, 0.2]],
        }
        self.mock_collection.query.return_value = mock_results

        # Act
        await self.rag_service.query(question=question)

        # Assert - Check user prompt structure
        completion_call = self.mock_llm_factory.execute_operation.call_args_list[1]
        user_prompt = completion_call[1]["user_prompt"]

        assert user_prompt.startswith("Question: How do I create a WordPress plugin?")
        assert "Context:\n" in user_prompt
        assert "Document 1 content" in user_prompt
        assert "Document 2 content" in user_prompt
