from enum import Enum


class LLMOperation(Enum):
    """Enumeration of LLM operations."""

    EMBEDDING = "embedding"
    COMPLETION = "completion"
