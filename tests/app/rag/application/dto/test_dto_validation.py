"""
Unit tests for DTO classes validation and serialization.

This module contains comprehensive tests for all DTO classes in the RAG application,
covering validation, serialization, and edge cases.
"""

import pytest
from pydantic import ValidationError

from app.rag.application.dto import (
    LLMCompletionResponse,
    ProcessedDocument,
    RAGQueryRequestDTO,
    RAGQueryResponseDTO,
    RAGSourceDTO,
    WordPressAPIResponse,
)


class TestRAGQueryRequestDTO:
    """Test cases for RAGQueryRequestDTO class."""

    def test_valid_request(self) -> None:
        """Test valid RAG query request creation."""
        request = RAGQueryRequestDTO(question="How do I create a WordPress plugin?")

        assert request.question == "How do I create a WordPress plugin?"

    def test_empty_question(self) -> None:
        """Test RAG query request with empty question."""
        request = RAGQueryRequestDTO(question="")

        assert request.question == ""

    def test_question_with_special_characters(self) -> None:
        """Test RAG query request with special characters."""
        question = "What's the best way to handle WordPress hooks & filters?"
        request = RAGQueryRequestDTO(question=question)

        assert request.question == question

    def test_question_with_unicode(self) -> None:
        """Test RAG query request with unicode characters."""
        question = "¿Cómo crear un plugin de WordPress?"
        request = RAGQueryRequestDTO(question=question)

        assert request.question == question

    def test_missing_question_field(self) -> None:
        """Test RAG query request with missing required field."""
        with pytest.raises(ValidationError) as exc_info:
            RAGQueryRequestDTO()

        assert "question" in str(exc_info.value)

    def test_question_not_string(self) -> None:
        """Test RAG query request with non-string question."""
        with pytest.raises(ValidationError) as exc_info:
            RAGQueryRequestDTO(question=123)

        assert "question" in str(exc_info.value)


class TestRAGSourceDTO:
    """Test cases for RAGSourceDTO class."""

    def test_valid_source(self) -> None:
        """Test valid RAG source creation."""
        source = RAGSourceDTO(
            title="WordPress Plugin Development",
            url="https://developer.wordpress.org/plugins/",
        )

        assert source.title == "WordPress Plugin Development"
        assert source.url == "https://developer.wordpress.org/plugins/"

    def test_empty_title(self) -> None:
        """Test RAG source with empty title."""
        source = RAGSourceDTO(title="", url="https://example.com")

        assert source.title == ""
        assert source.url == "https://example.com"

    def test_empty_url(self) -> None:
        """Test RAG source with empty URL."""
        source = RAGSourceDTO(title="Test Title", url="")

        assert source.title == "Test Title"
        assert source.url == ""

    def test_missing_title_field(self) -> None:
        """Test RAG source with missing title field."""
        with pytest.raises(ValidationError) as exc_info:
            RAGSourceDTO(url="https://example.com")

        assert "title" in str(exc_info.value)

    def test_missing_url_field(self) -> None:
        """Test RAG source with missing URL field."""
        with pytest.raises(ValidationError) as exc_info:
            RAGSourceDTO(title="Test Title")

        assert "url" in str(exc_info.value)

    def test_title_not_string(self) -> None:
        """Test RAG source with non-string title."""
        with pytest.raises(ValidationError) as exc_info:
            RAGSourceDTO(title=123, url="https://example.com")

        assert "title" in str(exc_info.value)

    def test_url_not_string(self) -> None:
        """Test RAG source with non-string URL."""
        with pytest.raises(ValidationError) as exc_info:
            RAGSourceDTO(title="Test Title", url=123)

        assert "url" in str(exc_info.value)


class TestRAGQueryResponseDTO:
    """Test cases for RAGQueryResponseDTO class."""

    def test_valid_response(self) -> None:
        """Test valid RAG query response creation."""
        sources = [
            RAGSourceDTO(title="Plugin Development", url="https://example.com/plugin"),
            RAGSourceDTO(title="WordPress Basics", url="https://example.com/basics"),
        ]
        response = RAGQueryResponseDTO(
            answer="To create a WordPress plugin, you need to create a PHP file.",
            sources=sources,
        )

        assert (
            response.answer
            == "To create a WordPress plugin, you need to create a PHP file."
        )
        assert len(response.sources) == 2
        assert response.sources[0].title == "Plugin Development"
        assert response.sources[1].title == "WordPress Basics"

    def test_response_with_empty_sources(self) -> None:
        """Test RAG query response with empty sources list."""
        response = RAGQueryResponseDTO(
            answer="I don't have enough information.", sources=[]
        )

        assert response.answer == "I don't have enough information."
        assert response.sources == []

    def test_response_with_empty_answer(self) -> None:
        """Test RAG query response with empty answer."""
        sources = [RAGSourceDTO(title="Test", url="https://example.com")]
        response = RAGQueryResponseDTO(answer="", sources=sources)

        assert response.answer == ""
        assert len(response.sources) == 1

    def test_missing_answer_field(self) -> None:
        """Test RAG query response with missing answer field."""
        sources = [RAGSourceDTO(title="Test", url="https://example.com")]

        with pytest.raises(ValidationError) as exc_info:
            RAGQueryResponseDTO(sources=sources)

        assert "answer" in str(exc_info.value)

    def test_missing_sources_field(self) -> None:
        """Test RAG query response with missing sources field."""
        with pytest.raises(ValidationError) as exc_info:
            RAGQueryResponseDTO(answer="Test answer")

        assert "sources" in str(exc_info.value)

    def test_answer_not_string(self) -> None:
        """Test RAG query response with non-string answer."""
        sources = [RAGSourceDTO(title="Test", url="https://example.com")]

        with pytest.raises(ValidationError) as exc_info:
            RAGQueryResponseDTO(answer=123, sources=sources)

        assert "answer" in str(exc_info.value)

    def test_sources_not_list(self) -> None:
        """Test RAG query response with non-list sources."""
        with pytest.raises(ValidationError) as exc_info:
            RAGQueryResponseDTO(answer="Test answer", sources="not a list")

        assert "sources" in str(exc_info.value)

    def test_model_dump(self) -> None:
        """Test RAG query response model_dump method."""
        sources = [
            RAGSourceDTO(title="Plugin Development", url="https://example.com/plugin"),
            RAGSourceDTO(title="WordPress Basics", url="https://example.com/basics"),
        ]
        response = RAGQueryResponseDTO(
            answer="To create a WordPress plugin, you need to create a PHP file.",
            sources=sources,
        )

        result = response.model_dump()

        expected = {
            "answer": "To create a WordPress plugin, you need to create a PHP file.",
            "sources": [
                {"title": "Plugin Development", "url": "https://example.com/plugin"},
                {"title": "WordPress Basics", "url": "https://example.com/basics"},
            ],
        }

        assert result == expected


class TestWordPressAPIResponse:
    """Test cases for WordPressAPIResponse class."""

    def test_valid_response(self) -> None:
        """Test valid WordPress API response creation."""
        response = WordPressAPIResponse(
            id=123,
            link="https://developer.wordpress.org/plugins/",
            title={"rendered": "Plugin Development"},
            content={"rendered": "<p>Plugin development guide</p>"},
            excerpt={"rendered": "Plugin development excerpt"},
            date="2023-01-01T00:00:00",
            modified="2023-01-02T00:00:00",
            slug="plugin-development",
            status="publish",
        )

        assert response.id == 123
        assert response.link == "https://developer.wordpress.org/plugins/"
        assert response.title == {"rendered": "Plugin Development"}
        assert response.content == {"rendered": "<p>Plugin development guide</p>"}
        assert response.excerpt == {"rendered": "Plugin development excerpt"}
        assert response.date == "2023-01-01T00:00:00"
        assert response.modified == "2023-01-02T00:00:00"
        assert response.slug == "plugin-development"
        assert response.status == "publish"

    def test_minimal_response(self) -> None:
        """Test WordPress API response with only required fields."""
        response = WordPressAPIResponse(
            id=123,
            link="https://developer.wordpress.org/plugins/",
            title={"rendered": "Plugin Development"},
            content={"rendered": "<p>Plugin development guide</p>"},
        )

        assert response.id == 123
        assert response.link == "https://developer.wordpress.org/plugins/"
        assert response.title == {"rendered": "Plugin Development"}
        assert response.content == {"rendered": "<p>Plugin development guide</p>"}
        assert response.excerpt is None
        assert response.date is None
        assert response.modified is None
        assert response.slug is None
        assert response.status is None

    def test_missing_required_fields(self) -> None:
        """Test WordPress API response with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            WordPressAPIResponse(
                link="https://developer.wordpress.org/plugins/",
                title={"rendered": "Plugin Development"},
                content={"rendered": "<p>Plugin development guide</p>"},
            )

        assert "id" in str(exc_info.value)

    def test_id_not_integer(self) -> None:
        """Test WordPress API response with non-integer ID."""
        with pytest.raises(ValidationError) as exc_info:
            WordPressAPIResponse(
                id="not_an_integer",
                link="https://developer.wordpress.org/plugins/",
                title={"rendered": "Plugin Development"},
                content={"rendered": "<p>Plugin development guide</p>"},
            )

        assert "id" in str(exc_info.value)

    def test_link_not_string(self) -> None:
        """Test WordPress API response with non-string link."""
        with pytest.raises(ValidationError) as exc_info:
            WordPressAPIResponse(
                id=123,
                link=123,
                title={"rendered": "Plugin Development"},
                content={"rendered": "<p>Plugin development guide</p>"},
            )

        assert "link" in str(exc_info.value)

    def test_title_not_dict(self) -> None:
        """Test WordPress API response with non-dict title."""
        with pytest.raises(ValidationError) as exc_info:
            WordPressAPIResponse(
                id=123,
                link="https://developer.wordpress.org/plugins/",
                title="not a dict",
                content={"rendered": "<p>Plugin development guide</p>"},
            )

        assert "title" in str(exc_info.value)

    def test_content_not_dict(self) -> None:
        """Test WordPress API response with non-dict content."""
        with pytest.raises(ValidationError) as exc_info:
            WordPressAPIResponse(
                id=123,
                link="https://developer.wordpress.org/plugins/",
                title={"rendered": "Plugin Development"},
                content="not a dict",
            )

        assert "content" in str(exc_info.value)


class TestProcessedDocument:
    """Test cases for ProcessedDocument class."""

    def test_valid_document(self) -> None:
        """Test valid processed document creation."""
        document = ProcessedDocument(
            id="123",
            title="WordPress Plugin Development",
            url="https://developer.wordpress.org/plugins/",
            content="<p>Plugin development guide content</p>",
        )

        assert document.id == "123"
        assert document.title == "WordPress Plugin Development"
        assert document.url == "https://developer.wordpress.org/plugins/"
        assert document.content == "<p>Plugin development guide content</p>"

    def test_document_with_empty_fields(self) -> None:
        """Test processed document with empty fields."""
        document = ProcessedDocument(id="", title="", url="", content="")

        assert document.id == ""
        assert document.title == ""
        assert document.url == ""
        assert document.content == ""

    def test_missing_required_fields(self) -> None:
        """Test processed document with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessedDocument(
                title="WordPress Plugin Development",
                url="https://developer.wordpress.org/plugins/",
                content="<p>Plugin development guide content</p>",
            )

        assert "id" in str(exc_info.value)

    def test_id_not_string(self) -> None:
        """Test processed document with non-string ID."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessedDocument(
                id=123,
                title="WordPress Plugin Development",
                url="https://developer.wordpress.org/plugins/",
                content="<p>Plugin development guide content</p>",
            )

        assert "id" in str(exc_info.value)

    def test_title_not_string(self) -> None:
        """Test processed document with non-string title."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessedDocument(
                id="123",
                title=123,
                url="https://developer.wordpress.org/plugins/",
                content="<p>Plugin development guide content</p>",
            )

        assert "title" in str(exc_info.value)

    def test_url_not_string(self) -> None:
        """Test processed document with non-string URL."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessedDocument(
                id="123",
                title="WordPress Plugin Development",
                url=123,
                content="<p>Plugin development guide content</p>",
            )

        assert "url" in str(exc_info.value)

    def test_content_not_string(self) -> None:
        """Test processed document with non-string content."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessedDocument(
                id="123",
                title="WordPress Plugin Development",
                url="https://developer.wordpress.org/plugins/",
                content=123,
            )

        assert "content" in str(exc_info.value)


class TestLLMCompletionResponse:
    """Test cases for LLMCompletionResponse class."""

    def test_valid_response(self) -> None:
        """Test valid LLM completion response creation."""
        response = LLMCompletionResponse(
            answer="This is a test answer",
            was_truncated=False,
            token_count=50,
            finish_reason="stop",
        )

        assert response.answer == "This is a test answer"
        assert response.was_truncated is False
        assert response.token_count == 50
        assert response.finish_reason == "stop"

    def test_minimal_response(self) -> None:
        """Test LLM completion response with only required fields."""
        response = LLMCompletionResponse(answer="This is a test answer")

        assert response.answer == "This is a test answer"
        assert response.was_truncated is False
        assert response.token_count is None
        assert response.finish_reason is None

    def test_response_with_defaults(self) -> None:
        """Test LLM completion response with default values."""
        response = LLMCompletionResponse(
            answer="This is a test answer",
            was_truncated=True,
            token_count=100,
            finish_reason="length",
        )

        assert response.answer == "This is a test answer"
        assert response.was_truncated is True
        assert response.token_count == 100
        assert response.finish_reason == "length"

    def test_missing_required_field(self) -> None:
        """Test LLM completion response with missing required field."""
        with pytest.raises(TypeError):
            LLMCompletionResponse()

    def test_answer_not_string(self) -> None:
        """Test LLM completion response with non-string answer."""
        # Dataclasses don't validate types at runtime, so this will succeed
        response = LLMCompletionResponse(answer=123)  # type: ignore
        assert response.answer == 123

    def test_was_truncated_not_boolean(self) -> None:
        """Test LLM completion response with non-boolean was_truncated."""
        # Dataclasses don't validate types at runtime, so this will succeed
        response = LLMCompletionResponse(answer="Test", was_truncated="not_boolean")  # type: ignore
        assert response.was_truncated == "not_boolean"

    def test_token_count_not_integer(self) -> None:
        """Test LLM completion response with non-integer token_count."""
        # Dataclasses don't validate types at runtime, so this will succeed
        response = LLMCompletionResponse(answer="Test", token_count="not_integer")  # type: ignore
        assert response.token_count == "not_integer"

    def test_finish_reason_not_string(self) -> None:
        """Test LLM completion response with non-string finish_reason."""
        # Dataclasses don't validate types at runtime, so this will succeed
        response = LLMCompletionResponse(answer="Test", finish_reason=123)  # type: ignore
        assert response.finish_reason == 123

    def test_str_method(self) -> None:
        """Test LLM completion response __str__ method."""
        response = LLMCompletionResponse(
            answer="This is a test answer",
            was_truncated=True,
            token_count=50,
            finish_reason="length",
        )

        assert str(response) == "This is a test answer"
