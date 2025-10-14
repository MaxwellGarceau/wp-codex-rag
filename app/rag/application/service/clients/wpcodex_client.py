from typing import Any

import httpx
from sentence_transformers import SentenceTransformer

from app.rag.application.dto import ProcessedDocument, WordPressAPIResponse
from app.rag.domain.interface.ingest_documentation_client import (
    IngestDocumentationClient,
)
from core.helpers.html_cleaner import HTMLCleaner
from core.helpers.semantic_chunker import SemanticChunker
from core.logging_config import get_logger

logger = get_logger(__name__)


class WPCodexClient(IngestDocumentationClient):
    """
    WordPress Codex client for fetching, processing, and embedding documentation.

    This client implements the IngestDocumentationClient interface and is specifically
    designed for WordPress Codex operations:
    - Fetching documentation from WordPress.org APIs (plugin-handbook, theme-handbook, etc.)
    - Chunking content for optimal embedding
    - Generating embeddings using local SentenceTransformer models
    - Processing documentation for vector database ingestion

    Public Interface:
        - process_documentation(section): Main method to process WordPress documentation
          Supported sections are defined in ENDPOINT_MAPPING class constant

    Internal Methods (use _ prefix):
        - _fetch_wp_docs(endpoint): Fetch documentation from WordPress API
        - _validate_http_response(): Validate HTTP responses and handle status codes
        - _parse_json_response(): Parse JSON responses with error handling
        - _chunk_text(): Split text into overlapping chunks (legacy)
        - semantic_chunker: SemanticChunker instance for intelligent text chunking
        - _generate_embeddings_batch(): Generate embeddings for text chunks
    """

    # Class constants
    WP_BASE_API = "https://developer.wordpress.org/wp-json/wp/v2"

    # Mapping of section names to WordPress API endpoints
    ENDPOINT_MAPPING = {
        "plugin": "plugin-handbook",
        # "theme": "theme-handbook",  # Future support
        # "api": "api-reference",     # Future support
    }

    def __init__(self) -> None:
        """Initialize the WP Codex client with embedding model and HTML cleaner."""
        logger.info("Initializing WP Codex client...")

        # Initialize embedding model for local processing
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded: all-MiniLM-L6-v2")

        # Initialize HTML cleaner for processing WordPress content
        self.html_cleaner = HTMLCleaner()
        logger.info("HTML cleaner initialized")

        # Initialize semantic chunker for intelligent text chunking
        self.semantic_chunker = SemanticChunker()
        logger.info("Semantic chunker initialized")

    async def _fetch_wp_docs(self, endpoint: str) -> list[ProcessedDocument]:
        """
        Fetch WordPress documentation from the official API.

        Args:
            endpoint: The API endpoint to fetch from (e.g., "plugin-handbook")

        Returns:
            List of processed documentation entries
        """
        docs: list[ProcessedDocument] = []
        page = 1
        per_page = 50

        api_url = f"{self.WP_BASE_API}/{endpoint}"
        logger.info(f"Fetching WordPress {endpoint} documentation from {api_url}...")

        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                try:
                    resp = await client.get(
                        api_url, params={"page": page, "per_page": per_page}
                    )

                    # Validate HTTP response and handle status codes
                    should_continue = self._validate_http_response(resp, page, api_url)
                    if not should_continue:
                        break

                    # Parse JSON response
                    items = self._parse_json_response(resp, page)

                    if not items:
                        logger.debug(f"No items returned for page {page}")
                        break

                    for item_data in items:
                        try:
                            # Validate API response against contract
                            api_response = WordPressAPIResponse(**item_data)

                            # Extract and process the data
                            doc_id = (
                                str(api_response.id)
                                if api_response.id
                                else api_response.link
                            )
                            title = api_response.title.get(
                                "rendered", "WordPress Documentation"
                            )
                            content_html = api_response.content.get("rendered", "")

                            # Create processed document
                            processed_doc = ProcessedDocument(
                                id=doc_id,
                                title=title,
                                url=api_response.link,
                                content=content_html,
                            )

                            docs.append(processed_doc)

                        except Exception as validation_error:
                            logger.warning(
                                f"Failed to validate API response item: {validation_error}"
                            )
                            # Fallback to manual extraction for malformed responses
                            doc_id = str(item_data.get("id", "")) or item_data.get(
                                "link", ""
                            )
                            title_obj = item_data.get("title", {})
                            content_obj = item_data.get("content", {})
                            title = title_obj.get("rendered", "WordPress Documentation")
                            content_html = content_obj.get("rendered", "")

                            docs.append(
                                ProcessedDocument(
                                    id=doc_id,
                                    title=title,
                                    url=item_data.get("link", ""),
                                    content=content_html,
                                )
                            )

                    page += 1
                    logger.debug(
                        f"Fetched page {page-1}, total docs so far: {len(docs)}"
                    )

                except httpx.HTTPStatusError as e:
                    logger.error(
                        f"HTTP status error fetching page {page}: {e.response.status_code} - {e}"
                    )
                    # Re-raise to let the caller handle the error appropriately
                    raise
                except httpx.RequestError as e:
                    logger.error(f"Request error fetching page {page}: {e}")
                    # Network/connection issues - might be retryable
                    raise
                except httpx.HTTPError as e:
                    logger.error(f"HTTP error fetching page {page}: {e}")
                    # Other HTTP errors
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error fetching page {page}: {e}")
                    # Unexpected errors - re-raise to preserve stack trace
                    raise

        logger.info(f"Successfully fetched {len(docs)} documentation entries")
        return docs

    def _chunk_text(
        self, text: str, chunk_size: int = 1200, overlap: int = 200
    ) -> list[str]:
        """
        Split text into overlapping chunks for better embedding quality.

        Args:
            text: The text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks

        Returns:
            List of text chunks
        """
        chunks: list[str] = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
            if start < 0:
                start = 0

        return chunks

    # Keep this method here for now
    # Let's not break it out while the project is still small
    def _validate_http_response(
        self, resp: httpx.Response, page: int, api_url: str
    ) -> bool:
        """
        Validate HTTP response and handle different status codes.

        Args:
            resp: The HTTP response to validate
            page: Current page number for logging
            api_url: The API URL for error messages

        Returns:
            bool: True if pagination should continue, False if pagination should stop

        Raises:
            httpx.HTTPStatusError: For various HTTP error status codes
        """
        # Handle specific status codes
        if resp.status_code == 400 and "rest_post_invalid_page_number" in resp.text:
            # No more pages - this is expected behavior
            logger.debug(f"Reached end of pagination at page {page}")
            return False  # Stop pagination
        elif resp.status_code == 404:
            logger.error(f"WordPress API endpoint not found: {api_url}")
            raise httpx.HTTPStatusError(
                f"Endpoint not found: {api_url}", request=resp.request, response=resp
            )
        elif resp.status_code == 429:
            logger.error(f"Rate limited by WordPress API. Status: {resp.status_code}")
            raise httpx.HTTPStatusError(
                "Rate limited by WordPress API", request=resp.request, response=resp
            )
        elif resp.status_code >= 500:
            logger.error(f"WordPress API server error. Status: {resp.status_code}")
            raise httpx.HTTPStatusError(
                f"WordPress API server error: {resp.status_code}",
                request=resp.request,
                response=resp,
            )
        elif resp.status_code >= 400:
            logger.error(f"WordPress API client error. Status: {resp.status_code}")
            raise httpx.HTTPStatusError(
                f"WordPress API client error: {resp.status_code}",
                request=resp.request,
                response=resp,
            )

        # If we get here, status is 2xx
        resp.raise_for_status()  # This should not raise for 2xx status codes
        return True  # Continue pagination

    def _parse_json_response(
        self, resp: httpx.Response, page: int
    ) -> list[dict[str, Any]]:
        """
        Parse JSON response with error handling.

        Args:
            resp: The HTTP response to parse
            page: Current page number for logging

        Returns:
            Parsed JSON data as a list of dictionaries

        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            items = resp.json()
            return items
        except ValueError as json_error:
            logger.error(
                f"Failed to parse JSON response from page {page}: {json_error}"
            )
            raise ValueError(f"Invalid JSON response from WordPress API: {json_error}")

    def _generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts in batch for efficiency.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors
        """
        logger.debug(f"Generating embeddings for {len(texts)} texts in batch...")

        try:
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            embeddings_list = embeddings.tolist()
            logger.debug(f"Generated {len(embeddings_list)} embeddings")
            return embeddings_list

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    async def process_documentation(self, section: str = "plugin") -> dict[str, Any]:
        """
        Process WordPress documentation for a specific section.

        Args:
            section: The documentation section to process (e.g., "plugin" -> "plugin-handbook")

        Returns:
            Dictionary containing processed documentation data
        """
        # Map section to API endpoint
        if section not in self.ENDPOINT_MAPPING:
            raise ValueError(
                f"Unsupported section: {section}. Supported sections: {list(self.ENDPOINT_MAPPING.keys())}"
            )

        endpoint = self.ENDPOINT_MAPPING[section]

        # Fetch documentation
        docs = await self._fetch_wp_docs(endpoint)

        # Process documents into chunks
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, str]] = []

        for doc in docs:
            # Clean HTML content before chunking
            cleaned_content = self.html_cleaner.clean_html(doc.content)

            # Skip documents with no content after cleaning
            if not cleaned_content.strip():
                logger.warning(
                    f"Skipping document with no content after HTML cleaning: {doc.title}"
                )
                continue

            for idx, chunk in enumerate(
                self.semantic_chunker.chunk_text(cleaned_content)
            ):
                ids.append(f"{doc.id}#c{idx}")
                documents.append(chunk)
                metadatas.append({"title": doc.title, "url": doc.url})

        # Generate embeddings
        embeddings = self._generate_embeddings_batch(documents)

        return {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "embeddings": embeddings,
            "total_chunks": len(documents),
            "total_docs": len(docs),
        }
