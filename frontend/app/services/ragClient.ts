import { HttpClient } from "./httpClient";

export type RAGSource = { title: string; url: string };
export type RAGQueryResponse = { answer: string; sources: RAGSource[] };

// Error properties structure - matches backend ErrorDetail contract
export type ErrorProperties = {
  message: string;
  statusCode: number | string;
  type: string;
  providerCode: string;
};

// Complete error response structure - matches backend ErrorResponse contract
export type ErrorResponse = {
  error: ErrorProperties;
};

export class RAGClient {
	private readonly httpClient: HttpClient;

	constructor(baseUrl?: string) {
		this.httpClient = new HttpClient(baseUrl);
	}

	async query(question: string): Promise<RAGQueryResponse> {
		try {
			return await this.httpClient.post<RAGQueryResponse>("/api/v1/rag/query", { question });
		} catch (error) {
			// Log the actual error for debugging
			console.error('RAG Client Error:', error);
			throw error;
		}
	}
}

