from typing import Any

import chromadb
from chromadb.config import Settings
from dependency_injector.wiring import Provide, inject
from openai import OpenAI

from app.rag.application.dto import RAGQueryResponseDTO, RAGSourceDTO
from app.rag.domain.usecase.rag import RAGUseCase
from core.config import config


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
        embeds = self.llm.embeddings.create(
            input=[question], model=config.OPENAI_EMBEDDING_MODEL
        )
        query_embedding = embeds.data[0].embedding

        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=5, include=["metadatas", "documents", "distances"]
        )

        contexts: list[str] = []
        sources: list[RAGSourceDTO] = []
        for i in range(len(results.get("documents", [[]])[0])):
            doc = results["documents"][0][i]
            meta = results["metadatas"][0][i]
            title = meta.get("title", "WordPress Codex")
            url = meta.get("url", "")
            contexts.append(doc)
            sources.append(RAGSourceDTO(title=title, url=url))

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

        response = RAGQueryResponseDTO(answer=answer, sources=sources)
        return response.model_dump()

