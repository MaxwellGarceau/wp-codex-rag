interface RAGToggleProps {
  useRAG: boolean;
  onToggle: (useRAG: boolean) => void;
  disabled?: boolean;
}

export function RAGToggle({ useRAG, onToggle, disabled = false }: RAGToggleProps) {
  return (
    <div className="flex items-center space-x-3">
      <span className={`text-sm font-medium ${disabled ? 'text-gray-400' : 'text-gray-700'}`}>
        {useRAG ? 'With RAG' : 'Without RAG'}
      </span>
      <button
        onClick={() => onToggle(!useRAG)}
        disabled={disabled}
        className={`
          relative inline-flex h-6 w-11 items-center rounded-full transition-colors
          ${useRAG ? 'bg-blue-600' : 'bg-gray-200'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        role="switch"
        aria-checked={useRAG}
        aria-label={`Toggle ${useRAG ? 'off' : 'on'} RAG`}
      >
        <span
          className={`
            inline-block h-4 w-4 transform rounded-full bg-white transition-transform
            ${useRAG ? 'translate-x-6' : 'translate-x-1'}
          `}
        />
      </button>
    </div>
  );
}
