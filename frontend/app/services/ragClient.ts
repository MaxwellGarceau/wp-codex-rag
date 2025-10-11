export type RAGSource = { title: string; url: string };
export type RAGQueryResponse = { answer: string; sources: RAGSource[] };

export class RAGClient {
	private readonly baseUrl: string;

	constructor(baseUrl?: string) {
		this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
	}

	async query(question: string): Promise<RAGQueryResponse> {
		const res = await fetch(`${this.baseUrl}/api/v1/rag/query`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ question }),
		});
		if (!res.ok) {
			const t = await res.text();
			throw new Error(t || `HTTP ${res.status}`);
		}
		return (await res.json()) as RAGQueryResponse;
	}
}

