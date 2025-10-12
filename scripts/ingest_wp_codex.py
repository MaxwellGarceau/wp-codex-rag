import argparse
import asyncio
import sys
from pathlib import Path

import requests

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

# Import after path modification
from app.rag.application.service.clients.wpcodex_client import (
    WPCodexClient,
)  # noqa: E402
from core.config import config  # noqa: E402


class ChromaDBRESTClient:
    """ChromaDB client using REST API."""

    def __init__(self):
        self.base_url = (
            f"http://{config.CHROMA_SERVER_HOST}:{config.CHROMA_SERVER_PORT}"
        )
        self.collection_name = config.RAG_COLLECTION_NAME

    def _make_request(
        self, method: str, endpoint: str, data: dict | None = None
    ) -> dict:
        """Make a REST API request to ChromaDB."""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {e!s}") from e

    def create_collection(self) -> None:
        """Create a collection if it doesn't exist."""
        # Check if collection exists
        try:
            collections = self._make_request("GET", "/api/v1/collections")
            existing_collections = [
                col.get("name", "") for col in collections.get("data", [])
            ]
        except Exception:
            # If v1 API fails, assume collection doesn't exist
            existing_collections = []

        if self.collection_name not in existing_collections:
            # Create collection
            data = {
                "name": self.collection_name,
                "metadata": {"description": "WordPress Codex Plugin Documentation"},
            }
            try:
                self._make_request("POST", "/api/v1/collections", data)
                print(f"Created collection: {self.collection_name}")
            except Exception:
                print(
                    f"Collection {self.collection_name} will be created automatically"
                )
        else:
            print(f"Collection already exists: {self.collection_name}")

    def add_documents(
        self, ids: list, documents: list, metadatas: list, embeddings: list
    ) -> None:
        """Add documents to the collection."""
        data = {
            "collection_name": self.collection_name,
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "embeddings": embeddings,
        }

        self._make_request("POST", "/api/v1/collections/add", data)


async def ingest(section: str) -> None:
    """Ingest WordPress documentation using WPCodexClient and REST API."""

    # Initialize ChromaDB REST client
    chroma_client = ChromaDBRESTClient()

    # Create collection
    chroma_client.create_collection()

    # Initialize WP Codex client
    wpcodex_client = WPCodexClient()

    # Process documentation
    print(f"Processing WordPress {section} documentation...")
    processed_data = await wpcodex_client.process_documentation(section)

    print(f"Adding {processed_data['total_chunks']} chunks to ChromaDB collection...")

    # Add documents in batches to avoid overwhelming the server
    batch_size = 100
    total_chunks = processed_data["total_chunks"]

    for i in range(0, total_chunks, batch_size):
        end_idx = min(i + batch_size, total_chunks)
        batch_ids = processed_data["ids"][i:end_idx]
        batch_documents = processed_data["documents"][i:end_idx]
        batch_metadatas = processed_data["metadatas"][i:end_idx]
        batch_embeddings = processed_data["embeddings"][i:end_idx]

        print(
            f"Adding batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size} ({len(batch_ids)} chunks)..."
        )

        try:
            chroma_client.add_documents(
                ids=batch_ids,
                documents=batch_documents,
                metadatas=batch_metadatas,
                embeddings=batch_embeddings,
            )
        except Exception as e:
            print(f"Error adding batch {i//batch_size + 1}: {e}")
            raise

    print(
        f"Successfully ingested {processed_data['total_chunks']} chunks from "
        f"{processed_data['total_docs']} documents into collection '{config.RAG_COLLECTION_NAME}'."
    )


def main() -> None:
    """Main entry point for the ingestion script."""
    parser = argparse.ArgumentParser(
        description="Ingest WordPress Codex documentation into vector database"
    )
    parser.add_argument(
        "--section",
        default="plugin",
        choices=["plugin"],
        help="WordPress docs section to ingest",
    )
    args = parser.parse_args()

    try:
        asyncio.run(ingest(args.section))
    except KeyboardInterrupt:
        print("\nIngestion interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
