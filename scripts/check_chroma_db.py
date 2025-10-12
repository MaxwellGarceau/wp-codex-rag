#!/usr/bin/env python3
"""
ChromaDB Data Checker Script

This script provides various ways to check and explore data in ChromaDB.
It can count documents, show sample data, and perform text searches.
"""

import argparse
import sys
from pathlib import Path

import chromadb

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

# Import after path modification
from core.config import config  # noqa: E402


class ChromaDBChecker:
    """ChromaDB data checker utility."""

    def __init__(self):
        self.client = chromadb.HttpClient(
            host=config.CHROMA_SERVER_HOST,
            port=config.CHROMA_SERVER_PORT,
            settings=chromadb.Settings(allow_reset=True)
        )
        self.collection_name = config.RAG_COLLECTION_NAME

    def get_collection(self):
        """Get the ChromaDB collection."""
        try:
            return self.client.get_collection(self.collection_name)
        except Exception as e:
            print(f"Error getting collection '{self.collection_name}': {e}")
            sys.exit(1)

    def count_documents(self):
        """Count documents in the collection."""
        collection = self.get_collection()
        count = collection.count()
        print(f"Collection '{self.collection_name}' contains {count} documents")
        return count

    def show_sample_documents(self, limit: int = 3):
        """Show sample documents from the collection."""
        collection = self.get_collection()
        result = collection.peek(limit=limit)
        
        print(f"\nSample documents from '{self.collection_name}':")
        print("=" * 60)
        
        for i, doc in enumerate(result['documents']):
            print(f"\nDocument {i+1}:")
            print(f"ID: {result['ids'][i]}")
            print(f"Content: {doc[:200]}...")
            if result['metadatas'] and result['metadatas'][i]:
                print(f"Metadata: {result['metadatas'][i]}")
            print("-" * 40)

    def search_documents(self, query: str, n_results: int = 5):
        """Search for documents using text query."""
        collection = self.get_collection()
        
        print(f"\nSearching for: '{query}'")
        print("=" * 60)
        
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if not results['documents'] or not results['documents'][0]:
                print("No results found.")
                return
            
            print(f"Found {len(results['documents'][0])} results:")
            
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i]
                metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                
                print(f"\nResult {i+1} (Distance: {distance:.3f}):")
                print(f"ID: {results['ids'][0][i]}")
                print(f"Content: {doc[:300]}...")
                if metadata:
                    print(f"Metadata: {metadata}")
                print("-" * 40)
                
        except Exception as e:
            print(f"Error searching documents: {e}")

    def list_collections(self):
        """List all collections in ChromaDB."""
        try:
            collections = self.client.list_collections()
            print(f"\nAvailable collections:")
            print("=" * 30)
            for collection in collections:
                print(f"- {collection.name} (ID: {collection.id})")
        except Exception as e:
            print(f"Error listing collections: {e}")

    def collection_info(self):
        """Show detailed collection information."""
        collection = self.get_collection()
        
        print(f"\nCollection Information:")
        print("=" * 40)
        print(f"Name: {collection.name}")
        print(f"ID: {collection.id}")
        print(f"Count: {collection.count()}")
        print(f"Metadata: {collection.metadata}")


def main():
    """Main function to run the ChromaDB checker."""
    parser = argparse.ArgumentParser(description="Check ChromaDB data and collections")
    parser.add_argument(
        "--action",
        type=str,
        choices=["count", "sample", "search", "list", "info"],
        default="count",
        help="Action to perform (default: count)"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Search query (required for search action)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Number of results to show (default: 3)"
    )
    parser.add_argument(
        "--results",
        type=int,
        default=5,
        help="Number of search results (default: 5)"
    )
    
    args = parser.parse_args()
    
    checker = ChromaDBChecker()
    
    try:
        if args.action == "count":
            checker.count_documents()
        elif args.action == "sample":
            checker.show_sample_documents(args.limit)
        elif args.action == "search":
            if not args.query:
                print("Error: --query is required for search action")
                sys.exit(1)
            checker.search_documents(args.query, args.results)
        elif args.action == "list":
            checker.list_collections()
        elif args.action == "info":
            checker.collection_info()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
