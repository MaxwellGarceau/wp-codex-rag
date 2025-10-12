"""
Data Transfer Objects (DTOs) for the RAG application.

This package contains contracts and DTOs used throughout the RAG application
for data validation, serialization, and type safety.
"""

from .rag_response import RAGQueryResponseDTO, RAGSourceDTO
from .wordpress_api_contracts import ProcessedDocument, WordPressAPIResponse

__all__ = [
    "ProcessedDocument",
    "RAGQueryResponseDTO",
    "RAGSourceDTO",
    "WordPressAPIResponse",
]
