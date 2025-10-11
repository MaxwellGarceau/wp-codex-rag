from typing import Any

import chromadb
from chromadb.config import Settings
from dependency_injector.wiring import Provide, inject
from openai import OpenAI, RateLimitError, APIError

from app.rag.application.dto import RAGQueryResponseDTO, RAGSourceDTO
from app.rag.domain.usecase.rag import RAGUseCase
from core.config import config
from core.logging_config import get_logger

logger = get_logger(__name__)


class RAGService(RAGUseCase):
    def __init__(self) -> None:
        self.client = chromadb.Client(
            Settings(persist_directory=config.CHROMA_PERSIST_DIRECTORY)
        )
        self.collection = self.client.get_or_create_collection(
            name=config.RAG_COLLECTION_NAME
        )
        self.llm = OpenAI(api_key=config.OPENAI_API_KEY)

    async def query(self, *, question: str) -> dict[str, Any]:
        logger.info(f"Starting RAG query for question: {question[:100]}...")
        
        try:
            # Generate embeddings
            logger.debug("Generating embeddings for question")
            embeds = self.llm.embeddings.create(
                input=[question], model=config.OPENAI_EMBEDDING_MODEL
            )
            query_embedding = embeds.data[0].embedding
            logger.debug(f"Generated embedding with {len(query_embedding)} dimensions")

            # Query vector database
            logger.debug("Querying vector database for similar documents")
            results = self.collection.query(
                query_embeddings=[query_embedding], n_results=5, include=["metadatas", "documents", "distances"]
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
                "You are a helpful assistant answering questions about WordPress. "
                "Use only the provided context. If unsure, say you don't know."
            )
            context_block = "\n\n".join(contexts)
            user_prompt = f"Question: {question}\n\nContext:\n{context_block}"

            completion = self.llm.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            answer = completion.choices[0].message.content or ""
            logger.info(f"Generated answer with {len(answer)} characters")

            response = RAGQueryResponseDTO(answer=answer, sources=sources)
            logger.info("RAG query completed successfully")
            return response.model_dump()
            
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {str(e)}")
            # Re-raise the OpenAI error so it gets passed through to the frontend
            raise e
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            # Re-raise the OpenAI error so it gets passed through to the frontend
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in RAG query: {str(e)}", exc_info=True)
            # For other errors, wrap them in a generic message
            raise Exception(f"An error occurred while processing your request: {str(e)}")

