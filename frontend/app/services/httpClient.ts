/**
 * HTTP client for making API requests with standardized error handling
 */
export class HttpClient {
	private readonly baseUrl: string;

	constructor(baseUrl?: string) {
		this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
	}

	async post<T>(endpoint: string, data: any): Promise<T> {
		const res = await fetch(`${this.baseUrl}${endpoint}`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(data),
		});

		if (!res.ok) {
			const errorText = await res.text();
			let errorMessage = `HTTP ${res.status}: ${res.statusText}`;

			try {
				const errorData = JSON.parse(errorText);
				if (errorData.error) {
					// Pass the full structured error response
					errorMessage = JSON.stringify(errorData.error);
				}
			} catch {
				// If JSON parsing fails, use the raw text or default message
				errorMessage = JSON.stringify({
					message: errorText || errorMessage
				});
			}

			throw new Error(errorMessage);
		}

		return (await res.json()) as T;
	}
}
