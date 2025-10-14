interface QuestionFormProps {
  question: string;
  loading: boolean;
  onQuestionChange: (question: string) => void;
  onSubmit: () => void;
}

export function QuestionForm({ question, loading, onQuestionChange, onSubmit }: QuestionFormProps) {
  return (
    <section className="space-y-3">
      <textarea
        value={question}
        onChange={(e) => onQuestionChange(e.target.value)}
        placeholder="e.g. How do I register a custom post type in a plugin?"
        className="w-full min-h-[120px] rounded-md border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        onClick={onSubmit}
        disabled={loading || question.trim().length === 0}
        className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Thinking…" : "Ask"}
      </button>
    </section>
  );
}
