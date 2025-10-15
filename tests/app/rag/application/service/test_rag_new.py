"""
Tests for the new RAGService (vector DB operations only).
"""

from unittest.mock import MagicMock, patch

import pytest

from app.rag.application.service.rag import RAGService


class TestRAGService:
    """Test cases for the new RAGService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_chroma_client = MagicMock()
        self.mock_collection = MagicMock()

        with patch("app.rag.application.service.rag.chromadb") as mock_chromadb:
            mock_chromadb.HttpClient.return_value = self.mock_chroma_client
            self.mock_chroma_client.get_or_create_collection.return_value = (
                self.mock_collection
            )
            self.rag_service = RAGService()

    def test_init(self) -> None:
        """Test RAGService initialization."""
        assert self.rag_service.client == self.mock_chroma_client
        assert self.rag_service.collection == self.mock_collection

    def test_query_vector_db_successful(self) -> None:
        """Test successful vector database query."""
        # Arrange
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
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
        contexts, sources = self.rag_service.query_vector_db(query_embedding)

        # Assert
        assert len(contexts) == 2
        assert contexts[0] == "Document 1 content"
        assert contexts[1] == "Document 2 content"

        assert len(sources) == 2
        assert sources[0].title == "Plugin Development"
        assert sources[0].url == "https://example.com/plugin-dev"
        assert sources[1].title == "WordPress Basics"
        assert sources[1].url == "https://example.com/wp-basics"

        # Verify collection query was called correctly
        self.mock_collection.query.assert_called_once_with(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["metadatas", "documents", "distances"],
        )

    def test_query_vector_db_no_documents(self) -> None:
        """Test vector database query with no documents found."""
        # Arrange
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_results = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }
        self.mock_collection.query.return_value = mock_results

        # Act
        contexts, sources = self.rag_service.query_vector_db(query_embedding)

        # Assert
        assert len(contexts) == 0
        assert len(sources) == 0

    def test_query_vector_db_missing_metadata(self) -> None:
        """Test vector database query with missing metadata fields."""
        # Arrange
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_results = {
            "documents": [["Document 1 content"]],
            "metadatas": [[{}]],  # Empty metadata
            "distances": [[0.1]],
        }
        self.mock_collection.query.return_value = mock_results

        # Act
        contexts, sources = self.rag_service.query_vector_db(query_embedding)

        # Assert
        assert len(contexts) == 1
        assert contexts[0] == "Document 1 content"

        assert len(sources) == 1
        assert sources[0].title == "WordPress Codex"  # Default title
        assert sources[0].url == ""  # Default empty URL

    def test_query_vector_db_chromadb_failure(self) -> None:
        """Test vector database query when ChromaDB fails."""
        # Arrange
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        self.mock_collection.query.side_effect = Exception("ChromaDB connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="ChromaDB connection failed"):
            self.rag_service.query_vector_db(query_embedding)
