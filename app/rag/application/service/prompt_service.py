"""
Centralized prompt management service.
"""


class PromptService:
    """Service for managing and generating prompts for different use cases."""

    @staticmethod
    def get_rag_system_prompt() -> str:
        """Get the system prompt for RAG-enabled responses."""
        return (
            "You are a WordPress expert assistant. Answer questions using ONLY the provided context. "
            "Keep responses SHORT and FOCUSED (2-3 sentences maximum). "
            "If the context doesn't contain the answer, say 'I don't have enough information in the provided context.' "
            "Do not add extra details or go beyond what's in the context."
        )

    @staticmethod
    def get_llm_only_system_prompt() -> str:
        """Get the system prompt for LLM-only responses."""
        return (
            "You are a WordPress expert assistant. Answer questions about WordPress development, "
            "plugin creation, theme development, and WordPress best practices. "
            "Keep responses concise and focused (2-3 sentences maximum). "
            "If you don't know the answer, say 'I don't have enough information to answer this question.'"
        )

    @staticmethod
    def build_rag_user_prompt(question: str, contexts: list[str]) -> str:
        """
        Build the user prompt for RAG responses with context.

        Args:
            question: The user's question
            contexts: List of context documents from the vector database

        Returns:
            Formatted user prompt with question and context
        """
        context_block = "\n\n".join(contexts)
        return f"Question: {question}\n\nContext:\n{context_block}"

    @staticmethod
    def build_llm_only_user_prompt(question: str) -> str:
        """
        Build the user prompt for LLM-only responses.

        Args:
            question: The user's question

        Returns:
            Formatted user prompt with just the question
        """
        return f"Question: {question}"
