# Vector Database

## What is a Vector Database?

A vector database is a specialized database designed to store, index, and search high-dimensional vectors (embeddings) efficiently. Unlike traditional databases that search for exact matches, vector databases use similarity metrics to find the most relevant vectors based on semantic meaning.

## ChromaDB in Our System

Our application uses ChromaDB as the vector database for storing WordPress Codex embeddings:

- **Storage**: Stores document chunks as vector embeddings alongside metadata (title, URL)
- **Indexing**: Creates efficient indexes for fast similarity search across high-dimensional vectors
- **Search**: Uses cosine similarity to find the most relevant document chunks for user queries
- **Persistence**: Data persists to disk via `CHROMA_PERSIST_DIRECTORY` configuration

## How It Works

1. **Ingestion**: WordPress Codex content is chunked and converted to embeddings via OpenAI API
2. **Storage**: Embeddings are stored in ChromaDB with associated metadata
3. **Query**: User questions are embedded and used to search for similar content
4. **Retrieval**: Most relevant chunks are returned for RAG processing

This enables semantic search over the entire WordPress Codex, finding relevant information based on meaning rather than exact keyword matches.
