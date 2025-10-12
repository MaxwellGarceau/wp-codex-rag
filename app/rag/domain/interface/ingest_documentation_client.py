"""
Abstract base class for documentation ingestion clients.

This module defines the interface that all documentation ingestion clients
must implement, providing a consistent contract for processing documentation
from various sources.
"""

from abc import ABC, abstractmethod
from typing import Any


class IngestDocumentationClient(ABC):
    """
    Abstract base class for documentation ingestion clients.

    This interface defines the contract that all documentation ingestion
    clients must implement, ensuring consistent behavior across different
    documentation sources (WordPress, GitBook, etc.).
    """

    @abstractmethod
    async def process_documentation(self, section: str = "default") -> dict[str, Any]:
        """
        Process documentation for a specific section.

        This method should:
        1. Fetch documentation from the source
        2. Process and chunk the content
        3. Generate embeddings
        4. Return structured data ready for vector database ingestion

        Args:
            section: The documentation section to process (e.g., "plugin", "theme", "api")

        Returns:
            Dictionary containing processed documentation data with keys:
            - ids: List of unique identifiers for each chunk
            - documents: List of text chunks
            - metadatas: List of metadata dictionaries for each chunk
            - embeddings: List of embedding vectors
            - total_chunks: Total number of chunks created
            - total_docs: Total number of documents processed

        Raises:
            ValueError: If the section is not supported
            httpx.HTTPError: If there are network/API errors
            Exception: For other processing errors
        """
        pass
