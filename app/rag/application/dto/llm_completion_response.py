from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMCompletionResponse:
    """Response object for LLM completion operations."""

    answer: str
    was_truncated: bool = False
    token_count: Optional[int] = None
    finish_reason: Optional[str] = None

    def __str__(self) -> str:
        """Return just the answer for backward compatibility."""
        return self.answer
