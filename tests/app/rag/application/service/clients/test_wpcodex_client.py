"""
Unit tests for WPCodexClient class.

This module contains comprehensive tests for the WPCodexClient class,
covering documentation processing, API interactions, error handling,
and integration with external services.
"""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from app.rag.application.dto import ProcessedDocument
from app.rag.application.service.clients.wpcodex_client import WPCodexClient


class TestWPCodexClient:
    """Test cases for WPCodexClient class."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for all tests in this class."""
        with patch(
            "app.rag.application.service.clients.wpcodex_client.SentenceTransformer"
        ) as mock_transformer, patch(
            "app.rag.application.service.clients.wpcodex_client.HTMLCleaner"
        ) as mock_html_cleaner, patch(
            "app.rag.application.service.clients.wpcodex_client.SemanticChunker"
        ) as mock_chunker:
            # Create mock instances that will be returned by the patched classes
            self.mock_transformer_instance = Mock()
            self.mock_html_cleaner_instance = Mock()
            self.mock_chunker_instance = Mock()

            # Configure the mocks to return our instances
            mock_transformer.return_value = self.mock_transformer_instance
            mock_html_cleaner.return_value = self.mock_html_cleaner_instance
            mock_chunker.return_value = self.mock_chunker_instance

            # Initialize client with mocked dependencies
            self.client = WPCodexClient()

            # Verify the client has the mocked instances
            assert self.client.embedding_model is self.mock_transformer_instance
            assert self.client.html_cleaner is self.mock_html_cleaner_instance
            assert self.client.semantic_chunker is self.mock_chunker_instance

            # Yield to allow tests to run
            yield

    def test_init(self) -> None:
        """Test WPCodexClient initialization."""
        assert hasattr(self.client, "embedding_model")
        assert hasattr(self.client, "html_cleaner")
        assert hasattr(self.client, "semantic_chunker")
        assert (
            self.client.WP_BASE_API == "https://developer.wordpress.org/wp-json/wp/v2"
        )
        assert "plugin" in self.client.ENDPOINT_MAPPING
        assert self.client.ENDPOINT_MAPPING["plugin"] == "plugin-handbook"

    def test_chunk_text_basic(self) -> None:
        """Test basic text chunking functionality."""
        text = "This is a test text that should be chunked properly with some overlap."
        chunks = self.client._chunk_text(text, chunk_size=20, overlap=5)

        assert len(chunks) > 1
        assert all(len(chunk) <= 20 for chunk in chunks)
        # Check overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            assert chunks[i][-5:] in chunks[i + 1] or chunks[i + 1][:5] in chunks[i]

    def test_chunk_text_empty(self) -> None:
        """Test text chunking with empty input."""
        chunks = self.client._chunk_text("")
        assert chunks == []


    def test_validate_http_response_success(self) -> None:
        """Test HTTP response validation for successful responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"

        result = self.client._validate_http_response(mock_response, 1, "test_url")
        assert result is True

    def test_validate_http_response_pagination_end(self) -> None:
        """Test HTTP response validation for pagination end."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "rest_post_invalid_page_number"

        result = self.client._validate_http_response(mock_response, 1, "test_url")
        assert result is False

    def test_validate_http_response_404(self) -> None:
        """Test HTTP response validation for 404 errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.request = Mock()

        with pytest.raises(httpx.HTTPStatusError, match="Endpoint not found"):
            self.client._validate_http_response(mock_response, 1, "test_url")

    def test_validate_http_response_429(self) -> None:
        """Test HTTP response validation for rate limiting."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limited"
        mock_response.request = Mock()

        with pytest.raises(
            httpx.HTTPStatusError, match="Rate limited by WordPress API"
        ):
            self.client._validate_http_response(mock_response, 1, "test_url")

    def test_validate_http_response_500(self) -> None:
        """Test HTTP response validation for server errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_response.request = Mock()

        with pytest.raises(httpx.HTTPStatusError, match="WordPress API server error"):
            self.client._validate_http_response(mock_response, 1, "test_url")

    def test_validate_http_response_400_other(self) -> None:
        """Test HTTP response validation for other 400 errors."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.request = Mock()

        with pytest.raises(httpx.HTTPStatusError, match="WordPress API client error"):
            self.client._validate_http_response(mock_response, 1, "test_url")

    def test_parse_json_response_success(self) -> None:
        """Test successful JSON response parsing."""
        mock_response = Mock()
        expected_data = [{"id": 1, "title": "Test"}]
        mock_response.json.return_value = expected_data

        result = self.client._parse_json_response(mock_response, 1)
        assert result == expected_data

    def test_parse_json_response_invalid_json(self) -> None:
        """Test JSON response parsing with invalid JSON."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with pytest.raises(
            ValueError, match="Invalid JSON response from WordPress API"
        ):
            self.client._parse_json_response(mock_response, 1)

    def test_generate_embeddings_batch_success(self) -> None:
        """Test successful batch embedding generation."""
        texts = ["Text 1", "Text 2", "Text 3"]
        expected_embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]

        # Mock the embedding model
        mock_embeddings = Mock()
        mock_embeddings.tolist.return_value = expected_embeddings
        self.mock_transformer_instance.encode.return_value = mock_embeddings

        result = self.client._generate_embeddings_batch(texts)

        assert result == expected_embeddings
        self.mock_transformer_instance.encode.assert_called_once_with(
            texts, show_progress_bar=True
        )

    def test_generate_embeddings_batch_failure(self) -> None:
        """Test batch embedding generation failure."""
        texts = ["Text 1", "Text 2"]
        self.mock_transformer_instance.encode.side_effect = Exception(
            "Embedding failed"
        )

        with pytest.raises(Exception, match="Embedding failed"):
            self.client._generate_embeddings_batch(texts)

    @pytest.mark.asyncio
    async def test_fetch_wp_docs_success(self) -> None:
        """Test successful WordPress documentation fetching."""
        # Mock API response data
        api_response_data = [
            {
                "id": 1,
                "link": "https://example.com/doc1",
                "title": {"rendered": "Document 1"},
                "content": {"rendered": "<p>Content 1</p>"},
                "excerpt": {"rendered": "Excerpt 1"},
                "date": "2023-01-01",
                "modified": "2023-01-02",
                "slug": "doc1",
                "status": "publish",
            },
            {
                "id": 2,
                "link": "https://example.com/doc2",
                "title": {"rendered": "Document 2"},
                "content": {"rendered": "<p>Content 2</p>"},
                "excerpt": None,
                "date": None,
                "modified": None,
                "slug": None,
                "status": None,
            },
        ]

        # Mock HTTP client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_response.json.return_value = api_response_data
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get = AsyncMock(return_value=mock_response)

            # Mock validation to return True for first page, False for second
            with patch.object(
                self.client, "_validate_http_response", side_effect=[True, False]
            ), patch.object(
                self.client, "_parse_json_response", return_value=api_response_data
            ):
                result = await self.client._fetch_wp_docs("plugin-handbook")

        assert len(result) == 2
        assert isinstance(result[0], ProcessedDocument)
        assert result[0].id == "1"
        assert result[0].title == "Document 1"
        assert result[0].url == "https://example.com/doc1"
        assert result[0].content == "<p>Content 1</p>"

        assert result[1].id == "2"
        assert result[1].title == "Document 2"
        assert result[1].url == "https://example.com/doc2"

    @pytest.mark.asyncio
    async def test_fetch_wp_docs_with_validation_error(self) -> None:
        """Test WordPress documentation fetching with validation error."""
        # Mock API response data with validation error
        api_response_data = [
            {
                "id": 1,
                "link": "https://example.com/doc1",
                "title": {"rendered": "Document 1"},
                "content": {"rendered": "<p>Content 1</p>"},
            }
        ]

        # Mock HTTP client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_response.json.return_value = api_response_data
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get = AsyncMock(return_value=mock_response)

            # Mock validation to return True for first page, False for second to stop loop
            with patch.object(
                self.client, "_validate_http_response", side_effect=[True, False]
            ), patch.object(
                self.client, "_parse_json_response", return_value=api_response_data
            ), patch(
                "app.rag.application.service.clients.wpcodex_client.WordPressAPIResponse"
            ) as mock_response_class:
                mock_response_class.side_effect = [
                    Exception("Validation error"),
                    None,
                ]

                result = await self.client._fetch_wp_docs("plugin-handbook")

        # Should have fallback processing for the first item
        assert len(result) == 1
        assert isinstance(result[0], ProcessedDocument)

    @pytest.mark.asyncio
    async def test_fetch_wp_docs_http_error(self) -> None:
        """Test WordPress documentation fetching with HTTP error."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "HTTP error", request=Mock(), response=Mock()
                )
            )

            with pytest.raises(httpx.HTTPStatusError):
                await self.client._fetch_wp_docs("plugin-handbook")

    @pytest.mark.asyncio
    async def test_fetch_wp_docs_request_error(self) -> None:
        """Test WordPress documentation fetching with request error."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get = AsyncMock(side_effect=httpx.RequestError("Request error"))

            with pytest.raises(httpx.RequestError):
                await self.client._fetch_wp_docs("plugin-handbook")

    @pytest.mark.asyncio
    async def test_process_documentation_success(self) -> None:
        """Test successful documentation processing."""
        # Mock documents
        mock_docs = [
            ProcessedDocument(
                id="1",
                title="Document 1",
                url="https://example.com/doc1",
                content="<p>Content 1</p>",
            ),
            ProcessedDocument(
                id="2",
                title="Document 2",
                url="https://example.com/doc2",
                content="<p>Content 2</p>",
            ),
        ]

        # Mock HTML cleaner
        self.mock_html_cleaner_instance.clean_html.side_effect = [
            "Cleaned content 1",
            "Cleaned content 2",
        ]

        # Mock semantic chunker
        self.mock_chunker_instance.chunk_text.side_effect = [
            ["Chunk 1.1", "Chunk 1.2"],
            ["Chunk 2.1"],
        ]

        # Mock embedding generation
        expected_embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        with patch.object(
            self.client, "_generate_embeddings_batch", return_value=expected_embeddings
        ), patch.object(self.client, "_fetch_wp_docs", return_value=mock_docs):
            result = await self.client.process_documentation("plugin")

        assert result["total_docs"] == 2
        assert result["total_chunks"] == 3
        assert len(result["ids"]) == 3
        assert len(result["documents"]) == 3
        assert len(result["metadatas"]) == 3
        assert len(result["embeddings"]) == 3

        # Check IDs
        assert result["ids"] == ["1#c0", "1#c1", "2#c0"]

        # Check documents
        assert result["documents"] == ["Chunk 1.1", "Chunk 1.2", "Chunk 2.1"]

        # Check metadata
        assert result["metadatas"][0]["title"] == "Document 1"
        assert result["metadatas"][0]["url"] == "https://example.com/doc1"
        assert result["metadatas"][1]["title"] == "Document 1"
        assert result["metadatas"][2]["title"] == "Document 2"

    @pytest.mark.asyncio
    async def test_process_documentation_empty_content(self) -> None:
        """Test documentation processing with empty content after cleaning."""
        # Mock documents with empty content
        mock_docs = [
            ProcessedDocument(
                id="1",
                title="Document 1",
                url="https://example.com/doc1",
                content="<p>Content 1</p>",
            ),
            ProcessedDocument(
                id="2",
                title="Document 2",
                url="https://example.com/doc2",
                content="<p>Content 2</p>",
            ),
        ]

        # Mock HTML cleaner to return empty content for second document
        self.mock_html_cleaner_instance.clean_html.side_effect = [
            "Cleaned content 1",
            "",
        ]

        # Mock semantic chunker
        self.mock_chunker_instance.chunk_text.return_value = ["Chunk 1.1"]

        # Mock embedding generation
        expected_embeddings = [[0.1, 0.2]]
        with patch.object(
            self.client, "_generate_embeddings_batch", return_value=expected_embeddings
        ), patch.object(self.client, "_fetch_wp_docs", return_value=mock_docs):
            result = await self.client.process_documentation("plugin")

        # Should skip the document with empty content
        assert result["total_docs"] == 2  # Original docs count
        assert result["total_chunks"] == 1  # Only one chunk from first doc
        assert len(result["ids"]) == 1
        assert result["ids"] == ["1#c0"]

    @pytest.mark.asyncio
    async def test_process_documentation_unsupported_section(self) -> None:
        """Test documentation processing with unsupported section."""
        with pytest.raises(ValueError, match="Unsupported section: invalid"):
            await self.client.process_documentation("invalid")

    @pytest.mark.asyncio
    async def test_process_documentation_fetch_error(self) -> None:
        """Test documentation processing when fetching fails."""
        with patch.object(
            self.client, "_fetch_wp_docs", side_effect=Exception("Fetch failed")
        ):
            with pytest.raises(Exception, match="Fetch failed"):
                await self.client.process_documentation("plugin")
