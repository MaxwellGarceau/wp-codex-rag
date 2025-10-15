/**
 * API Configuration
 * Centralized configuration for all API endpoints used across the application
 */

export const API_ENDPOINTS = {
  RAG: {
    QUERY: '/api/v1/rag/query',
    QUERY_LLM_ONLY: '/api/v1/rag/query-llm-only',
  },
} as const;

/**
 * API endpoint configuration for RAG operations
 */
export class ApiConfig {
  /**
   * Get the appropriate RAG query endpoint based on whether RAG is enabled
   * @param useRAG - Whether to use RAG-enhanced query or LLM-only query
   * @returns The appropriate endpoint path
   */
  static getRAGQueryEndpoint(useRAG: boolean): string {
    return useRAG ? API_ENDPOINTS.RAG.QUERY : API_ENDPOINTS.RAG.QUERY_LLM_ONLY;
  }
}
