import argparse
import asyncio
import json
from typing import Iterable

import chromadb
from chromadb.config import Settings
import httpx
from openai import OpenAI

from core.config import config


WP_PLUGIN_HANDBOOK_API = "https://developer.wordpress.org/wp-json/wp/v2/plugin-handbook"


async def fetch_wp_plugin_docs() -> list[dict]:
    # Fetch plugin handbook entries via official WP JSON API
    docs: list[dict] = []
    page = 1
    per_page = 50
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            resp = await client.get(
                WP_PLUGIN_HANDBOOK_API, params={"page": page, "per_page": per_page}
            )
            if resp.status_code == 400 and "rest_post_invalid_page_number" in resp.text:
                # No more pages
                break
            resp.raise_for_status()
            items = resp.json()
            if not items:
                break
            for item in items:
                # Typical WP fields: id, link, title.rendered, content.rendered
                doc_id = str(item.get("id", ""))
                link = item.get("link", "")
                title_obj = item.get("title", {})
                content_obj = item.get("content", {})
                title = title_obj.get("rendered", "Plugin Handbook")
                content_html = content_obj.get("rendered", "")
                docs.append(
                    {
                        "id": doc_id or link,
                        "title": title,
                        "url": link,
                        "content": content_html,
                    }
                )
            page += 1
    return docs


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


async def ingest(section: str) -> None:
    client = chromadb.Client(Settings(persist_directory=config.CHROMA_PERSIST_DIRECTORY))
    collection = client.get_or_create_collection(name=config.RAG_COLLECTION_NAME)

    openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

    if section == "plugin":
        docs = await fetch_wp_plugin_docs()
    else:
        raise ValueError("Unsupported section")

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for doc in docs:
        for idx, chunk in enumerate(chunk_text(doc["content"])):
            ids.append(f"{doc['id']}#c{idx}")
            documents.append(chunk)
            metadatas.append({"title": doc["title"], "url": doc["url"]})

    # Embed in small batches to avoid limits
    batch_size = 64
    embeddings: list[list[float]] = []
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        resp = openai_client.embeddings.create(input=batch, model=config.OPENAI_EMBEDDING_MODEL)
        embeddings.extend([d.embedding for d in resp.data])

    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    client.persist()
    print(f"Ingested {len(documents)} chunks into collection '{config.RAG_COLLECTION_NAME}'.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--section", default="plugin", choices=["plugin"], help="WordPress docs section")
    args = parser.parse_args()
    asyncio.run(ingest(args.section))


if __name__ == "__main__":
    main()

