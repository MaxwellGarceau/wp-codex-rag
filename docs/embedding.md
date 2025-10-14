# Embeddings

## What are Embeddings?

Embeddings are numerical representations of text that capture semantic meaning. They convert words, sentences, or documents into high-dimensional vectors where similar content has similar vector representations. This allows for semantic search, similarity comparisons, and retrieval-augmented generation (RAG).

## LLM Embedding Endpoint

Our application uses HuggingFace's sentence transformer model to convert WordPress Codex content into vector representations:

- **Model**: `all-MiniLM-L6-v2` (HuggingFace sentence transformer)
- **Purpose**: Convert documentation chunks into embeddings for vector storage
- **Storage**: Embeddings are stored in ChromaDB for efficient similarity search
- **Usage**: When users ask questions, we embed the query and find similar documentation chunks

The embedding process enables semantic search over the WordPress Codex, allowing users to find relevant information even when they don't use exact keywords from the documentation.
