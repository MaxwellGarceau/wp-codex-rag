import { RAGSource } from "../services/ragClient";
import { MarkdownRenderer } from "./MarkdownRenderer";

interface AnswerDisplayProps {
  answer: string;
  sources: RAGSource[];
}

export function AnswerDisplay({ answer, sources }: AnswerDisplayProps) {
  return (
    <section className="space-y-3">
      <h2 className="text-xl font-semibold">Answer</h2>
      <div className="rounded-md border border-gray-200 bg-white p-4">
        <MarkdownRenderer content={answer} />
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
  );
}
