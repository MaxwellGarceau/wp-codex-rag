"use client";
import { useState } from "react";
import { RAGClient, RAGSource } from "./services/ragClient";

const client = new RAGClient();

export default function HomePage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<RAGSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = async () => {
    setLoading(true);
    setError(null);
    setAnswer(null);
    setSources([]);
    try {
      const data = await client.query(question);
      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (e: any) {
      setError(e.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-3xl p-6 space-y-6">
      <header className="space-y-1">
        <h1 className="text-3xl font-semibold">WordPress Codex Q&A</h1>
        <p className="text-gray-600">Ask questions about plugin development.</p>
      </header>

      <section className="space-y-3">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. How do I register a custom post type in a plugin?"
          className="w-full min-h-[120px] rounded-md border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={ask}
          disabled={loading || question.trim().length === 0}
          className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Thinking…" : "Ask"}
        </button>
      </section>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-red-700">
          {error}
        </div>
      )}

      {answer && (
        <section className="space-y-3">
          <h2 className="text-xl font-semibold">Answer</h2>
          <div className="rounded-md border border-gray-200 bg-white p-4 whitespace-pre-wrap">
            {answer}
          </div>
          {sources.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-medium">Sources</h3>
              <ul className="list-disc pl-6 space-y-1">
                {sources.map((s, i) => (
                  <li key={`${s.url}-${i}`}>
                    <a href={s.url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                      {s.title}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
    </main>
  );
}

