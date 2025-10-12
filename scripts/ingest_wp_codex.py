import argparse
import asyncio
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings

from app.rag.application.service.clients.wpcodex_client import WPCodexClient
from core.config import config


async def ingest(section: str) -> None:
    """Ingest WordPress documentation using WPCodexClient."""

    # Initialize ChromaDB client
    client = chromadb.Client(
        Settings(persist_directory=config.CHROMA_PERSIST_DIRECTORY)
    )
    collection = client.get_or_create_collection(name=config.RAG_COLLECTION_NAME)

    # Initialize WP Codex client
    wpcodex_client = WPCodexClient()

    # Process documentation
    print(f"Processing WordPress {section} documentation...")
    processed_data = await wpcodex_client.process_documentation(section)

    print(f"Adding {processed_data['total_chunks']} chunks to ChromaDB collection...")
    collection.add(
        ids=processed_data["ids"],
        documents=processed_data["documents"],
        metadatas=processed_data["metadatas"],
        embeddings=processed_data["embeddings"],
    )

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
