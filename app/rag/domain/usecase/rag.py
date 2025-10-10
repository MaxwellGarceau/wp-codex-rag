from abc import ABC, abstractmethod
from typing import Any


class RAGUseCase(ABC):
    @abstractmethod
    async def query(self, *, question: str) -> dict[str, Any]:
        """Query the RAG system and return answer and sources."""

