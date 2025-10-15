import chromadb

from app.rag.application.dto import RAGSourceDTO
from core.config import config
from core.logging_config import get_logger

logger = get_logger(__name__)


class RAGService:
    """Service for vector database operations only."""

    def __init__(self) -> None:
        # Connect to ChromaDB server running in Docker
        self.client = chromadb.HttpClient(
            host=config.CHROMA_SERVER_HOST,
            port=config.CHROMA_SERVER_PORT,
            settings=chromadb.Settings(allow_reset=True),
        )
        self.collection = self.client.get_or_create_collection(
            name=config.RAG_COLLECTION_NAME
        )

    def query_vector_db(
        self, query_embedding: list[float]
    ) -> tuple[list[str], list[RAGSourceDTO]]:
        """
        Query the vector database for similar documents.

        Args:
            query_embedding: The embedding vector to search for

        Returns:
            Tuple of (contexts, sources) from the vector database
        """
        logger.debug("Querying vector database for similar documents")
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["metadatas", "documents", "distances"],
        )

        # Process results
        contexts: list[str] = []
        sources: list[RAGSourceDTO] = []
        num_docs = len(results.get("documents", [[]])[0])
        logger.info(f"Found {num_docs} relevant documents")

        for i in range(num_docs):
            doc = results["documents"][0][i]
            meta = results["metadatas"][0][i]
            title = meta.get("title", "WordPress Codex")
            url = meta.get("url", "")
            contexts.append(doc)
            sources.append(RAGSourceDTO(title=title, url=url))
            logger.debug(f"Added source: {title} ({url})")

        return contexts, sources
