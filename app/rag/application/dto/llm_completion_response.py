from dataclasses import dataclass


@dataclass
class LLMCompletionResponse:
    """Response object for LLM completion operations."""

    answer: str
    was_truncated: bool = False
    token_count: int | None = None
    finish_reason: str | None = None

    def __str__(self) -> str:
        """Return just the answer for backward compatibility."""
        return self.answer
