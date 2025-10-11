export type RAGSource = { title: string; url: string };
export type RAGQueryResponse = { answer: string; sources: RAGSource[] };

// This type must match the backend ErrorResponse contract exactly
export type ErrorResponse = {
  error: {
    message: string;
    type: string;
    param?: string | null;
    code?: string;
  };
};

export class RAGClient {
	private readonly baseUrl: string;

	constructor(baseUrl?: string) {
		this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
	}

	async query(question: string): Promise<RAGQueryResponse> {
		try {
			const res = await fetch(`${this.baseUrl}/api/v1/rag/query`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ question }),
			});
			
			if (!res.ok) {
				const errorText = await res.text();
				let errorMessage = `HTTP ${res.status}: ${res.statusText}`;

				try {
					const errorData = JSON.parse(errorText) as ErrorResponse;
					if (errorData.error?.message) {
						errorMessage = errorData.error.message;
					}
				} catch {
					// If JSON parsing fails, use the raw text or default message
					errorMessage = errorText || errorMessage;
				}

				throw new Error(errorMessage);
			}
			return (await res.json()) as RAGQueryResponse;
		} catch (error) {
			// Log the actual error for debugging
			console.error('RAG Client Error:', error);
			throw error;
		}
	}
}

