"""
RAG response DTOs for query results.
"""

from typing import Any

from pydantic import BaseModel


class RAGSourceDTO(BaseModel):
    """DTO for RAG source information."""

    title: str
    url: str


class RAGQueryResponseDTO(BaseModel):
    """DTO for RAG query response."""

    answer: str
    sources: list[RAGSourceDTO]

    def model_dump(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "answer": self.answer,
            "sources": [source.model_dump() for source in self.sources],
        }
