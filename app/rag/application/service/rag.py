from typing import Any

import chromadb

from app.rag.application.dto import RAGQueryResponseDTO, RAGSourceDTO
from app.rag.application.service.llm_service_factory import LLMServiceFactory
from app.rag.domain.enum.llm_operation import LLMOperation
from app.rag.domain.enum.llm_provider import LLMProvider
from app.rag.domain.usecase.rag import RAGUseCase
from core.config import config
from core.logging_config import get_logger

logger = get_logger(__name__)


class RAGService(RAGUseCase):
    def __init__(self, llm_service_factory: LLMServiceFactory) -> None:
        # Connect to ChromaDB server running in Docker
        self.client = chromadb.HttpClient(
            host=config.CHROMA_SERVER_HOST,
            port=config.CHROMA_SERVER_PORT,
            settings=chromadb.Settings(allow_reset=True),
        )
        self.collection = self.client.get_or_create_collection(
            name=config.RAG_COLLECTION_NAME
        )
        self.llm_factory = llm_service_factory

    async def query(self, *, question: str) -> dict[str, Any]:
        logger.info(f"Starting RAG query for question: {question[:100]}...")

        try:
            # Generate embeddings
            logger.debug("Generating embeddings for question")
            query_embedding = self.llm_factory.execute_operation(
                operation=LLMOperation.EMBEDDING,
                provider=LLMProvider.GROQ,
                text=question,
            )

            # Query vector database
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

            # Generate answer using LLM
            logger.debug("Generating answer using LLM")
            system_prompt = (
                "You are a WordPress expert assistant. Answer questions using ONLY the provided context. "
                "Keep responses SHORT and FOCUSED (2-3 sentences maximum). "
                "If the context doesn't contain the answer, say 'I don't have enough information in the provided context.' "
                "Do not add extra details or go beyond what's in the context."
            )
            context_block = "\n\n".join(contexts)
            user_prompt = f"Question: {question}\n\nContext:\n{context_block}"

            # Log the final assembled prompt for debugging
            logger.info(f"Final prompt length: {len(user_prompt)} characters")
            logger.debug(f"Final assembled prompt:\n{user_prompt}")

            answer = self.llm_factory.execute_operation(
                operation=LLMOperation.COMPLETION,
                provider=LLMProvider.GROQ,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,  # Lower temperature for more focused responses
                max_tokens=150,  # Much shorter responses
            )
            logger.info(f"Generated answer with {len(answer)} characters")

            response = RAGQueryResponseDTO(answer=answer, sources=sources)
            logger.info("RAG query completed successfully")
            return response.model_dump()

        except Exception as e:
            logger.error(f"Unexpected error in RAG query: {e!s}", exc_info=True)
            # Re-raise the original exception to preserve all its properties
            raise
