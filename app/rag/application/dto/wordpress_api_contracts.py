"""
WordPress API response contracts and data transfer objects.

This module defines the expected structure for WordPress API responses
and processed documents used by the WPCodexClient.
"""


from pydantic import BaseModel, Field


class WordPressAPIResponse(BaseModel):
    """
    Contract for WordPress API response structure.

    This model defines the expected fields from WordPress REST API responses,
    particularly for documentation endpoints like plugin-handbook.
    """

    id: int = Field(description="Unique identifier for the post/page")
    link: str = Field(description="URL to the post/page")
    title: dict[str, str] = Field(description="Title object with rendered content")
    content: dict[str, str | bool] = Field(description="Content object with rendered HTML")
    excerpt: dict[str, str] | None = Field(
        default=None, description="Excerpt object with rendered content"
    )
    date: str | None = Field(default=None, description="Publication date")
    modified: str | None = Field(default=None, description="Last modification date")
    slug: str | None = Field(default=None, description="URL slug")
    status: str | None = Field(default=None, description="Publication status")


class ProcessedDocument(BaseModel):
    """
    Contract for processed document structure.

    This model represents a document after it has been processed from
    the WordPress API response and is ready for embedding and storage.
    """

    id: str = Field(description="Unique identifier (post ID or link)")
    title: str = Field(description="Document title")
    url: str = Field(description="Document URL")
    content: str = Field(description="Document content (HTML)")
