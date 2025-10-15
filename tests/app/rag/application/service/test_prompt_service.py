"""
Tests for PromptService.
"""


from app.rag.application.service.prompt_service import PromptService


class TestPromptService:
    """Test cases for PromptService."""

    def test_get_rag_system_prompt(self) -> None:
        """Test get_rag_system_prompt method."""
        # Act
        prompt = PromptService.get_rag_system_prompt()

        # Assert
        assert isinstance(prompt, str)
        assert "WordPress expert assistant" in prompt
        assert "provided context" in prompt
        assert "SHORT and FOCUSED" in prompt

    def test_get_llm_only_system_prompt(self) -> None:
        """Test get_llm_only_system_prompt method."""
        # Act
        prompt = PromptService.get_llm_only_system_prompt()

        # Assert
        assert isinstance(prompt, str)
        assert "WordPress expert assistant" in prompt
        assert "WordPress development" in prompt
        assert "plugin creation" in prompt
        assert "theme development" in prompt

    def test_build_rag_user_prompt(self) -> None:
        """Test build_rag_user_prompt method."""
        # Arrange
        question = "How do I create a plugin?"
        contexts = ["Context 1", "Context 2", "Context 3"]

        # Act
        prompt = PromptService.build_rag_user_prompt(question, contexts)

        # Assert
        assert isinstance(prompt, str)
        assert f"Question: {question}" in prompt
        assert "Context:" in prompt
        assert "Context 1" in prompt
        assert "Context 2" in prompt
        assert "Context 3" in prompt

    def test_build_rag_user_prompt_empty_contexts(self) -> None:
        """Test build_rag_user_prompt with empty contexts."""
        # Arrange
        question = "How do I create a plugin?"
        contexts = []

        # Act
        prompt = PromptService.build_rag_user_prompt(question, contexts)

        # Assert
        assert isinstance(prompt, str)
        assert f"Question: {question}" in prompt
        assert "Context:" in prompt

    def test_build_llm_only_user_prompt(self) -> None:
        """Test build_llm_only_user_prompt method."""
        # Arrange
        question = "How do I create a plugin?"

        # Act
        prompt = PromptService.build_llm_only_user_prompt(question)

        # Assert
        assert isinstance(prompt, str)
        assert prompt == f"Question: {question}"

    def test_prompt_consistency(self) -> None:
        """Test that prompts are consistent across calls."""
        # Act
        rag_prompt_1 = PromptService.get_rag_system_prompt()
        rag_prompt_2 = PromptService.get_rag_system_prompt()

        llm_prompt_1 = PromptService.get_llm_only_system_prompt()
        llm_prompt_2 = PromptService.get_llm_only_system_prompt()

        # Assert
        assert rag_prompt_1 == rag_prompt_2
        assert llm_prompt_1 == llm_prompt_2
        assert rag_prompt_1 != llm_prompt_1
