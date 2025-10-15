"use client";
import { useState } from "react";
import { RAGClient, RAGSource } from "./services/ragClient";
import { ErrorDisplay } from "./components/ErrorDisplay";
import { Header } from "./components/Header";
import { QuestionForm } from "./components/QuestionForm";
import { AnswerDisplay } from "./components/AnswerDisplay";

const client = new RAGClient();

export default function HomePage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<RAGSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useRAG, setUseRAG] = useState(true);

  const ask = async () => {
    setLoading(true);
    setError(null);
    setAnswer(null);
    setSources([]);
    try {
      const data = await client.query(question, useRAG);
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
      <Header
        title="WordPress Codex Q&A"
        description="Ask questions about plugin development."
      />

      <QuestionForm
        question={question}
        loading={loading}
        useRAG={useRAG}
        onQuestionChange={setQuestion}
        onRAGToggle={setUseRAG}
        onSubmit={ask}
      />

      {error && (
        <ErrorDisplay
          error={error}
          onDismiss={() => setError(null)}
        />
      )}

      {answer && (
        <AnswerDisplay answer={answer} sources={sources} />
      )}
    </main>
  );
}
