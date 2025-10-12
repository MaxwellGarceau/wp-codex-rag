"""
Data Transfer Objects (DTOs) for the RAG application.

This package contains contracts and DTOs used throughout the RAG application
for data validation, serialization, and type safety.
"""

from .wordpress_api_contracts import ProcessedDocument, WordPressAPIResponse

__all__ = [
    "WordPressAPIResponse",
    "ProcessedDocument",
]
