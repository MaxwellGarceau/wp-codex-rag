import argparse
import asyncio
import sys
from pathlib import Path

import chromadb

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

# Import after path modification
from app.rag.application.service.clients.wpcodex_client import (  # noqa: E402
    WPCodexClient,
)
from core.config import config  # noqa: E402


class ChromaDBClient:
    """ChromaDB client using Python client library."""

    def __init__(self) -> None:
        self.client = chromadb.HttpClient(
            host=config.CHROMA_SERVER_HOST,
            port=config.CHROMA_SERVER_PORT,
            settings=chromadb.Settings(allow_reset=True),
        )
        self.collection_name = config.RAG_COLLECTION_NAME

    def create_collection(self) -> None:
        """Create a collection if it doesn't exist."""
        try:
            # Try to get existing collection
            self.client.get_collection(self.collection_name)
            print(f"Collection already exists: {self.collection_name}")
        except Exception:
            # Collection doesn't exist, create it
            try:
                self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "WordPress Codex Plugin Documentation"},
                )
                print(f"Created collection: {self.collection_name}")
            except Exception as e:
                # If collection already exists, that's fine
                if "already exists" in str(e):
                    print(f"Collection already exists: {self.collection_name}")
                else:
                    print(f"Error creating collection: {e}")
                    raise

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            collection = self.client.get_collection(self.collection_name)
            count_before = collection.count()
            if count_before > 0:
                print(
                    f"Clearing {count_before} existing documents from collection '{self.collection_name}'..."
                )
                # Delete all documents by getting all IDs and deleting them
                results = collection.get()
                if results["ids"]:
                    collection.delete(ids=results["ids"])
                    print(f"Successfully cleared {len(results['ids'])} documents")
                else:
                    print("Collection was already empty")
            else:
                print("Collection is already empty")
        except Exception as e:
            print(f"Error clearing collection: {e}")
            raise

    def add_documents(
        self, ids: list, documents: list, metadatas: list, embeddings: list
    ) -> None:
        """Add documents to the collection."""
        collection = self.client.get_collection(self.collection_name)
        collection.add(
            ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings
        )


async def ingest(section: str, clear_existing: bool = True) -> None:
    """Ingest WordPress documentation using WPCodexClient and ChromaDB client."""

    # Initialize ChromaDB client
    chroma_client = ChromaDBClient()

    # Create collection
    chroma_client.create_collection()

    # Clear existing data to prevent duplicates (if requested)
    if clear_existing:
        chroma_client.clear_collection()
    else:
        print("Skipping collection clearing - preserving existing data")

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
    """Main function to run the ingestion script."""
    parser = argparse.ArgumentParser(
        description="Ingest WordPress documentation into ChromaDB"
    )
    parser.add_argument(
        "--section",
        type=str,
        default="plugin",
        help="WordPress documentation section to ingest (default: plugin)",
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Skip clearing existing data from the collection (default: clear existing data)",
    )

    args = parser.parse_args()

    try:
        asyncio.run(ingest(args.section, clear_existing=not args.no_clear))
    except Exception as e:
        print(f"Error during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
