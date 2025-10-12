"""
Domain interfaces for the RAG application.

This package contains abstract base classes and interfaces that define
contracts for various components in the RAG system.
"""

from .ingest_documentation_client import IngestDocumentationClient
from .llm_client import LLMClientInterface

__all__ = [
    "IngestDocumentationClient",
    "LLMClientInterface",
]
