import { ErrorResponse } from "../services/ragClient";

interface ErrorDisplayProps {
  error: string;
  onDismiss?: () => void;
}

export function ErrorDisplay({ error, onDismiss }: ErrorDisplayProps) {
  const parseError = (error: string): { statusCode?: string; errorType?: string; message: string; code?: string; param?: string; errorData?: any } => {
    // Try to parse as structured error response first
    try {
      const errorData = JSON.parse(error) as any; // Use any since we add statusCode in RAG client
      if (errorData.error) {
        const { message, type, code, param } = errorData.error;
        return {
          statusCode: errorData.statusCode?.toString(),
          errorType: type,
          message,
          code,
          param,
          errorData
        };
      }
    } catch {
      // Not JSON, treat as plain text error
    }

    // For plain text errors, just display as-is
    return {
      message: error
    };
  };

  const { statusCode, errorType, message, code, param, errorData } = parseError(error);

  return (
    <div className="rounded-md border border-red-200 bg-red-50 p-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-red-400"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <div className="text-sm text-red-700">
            {statusCode && errorType && (
              <p className="font-mono font-medium mb-2">
                Error code: {statusCode} - {errorType}
              </p>
            )}
            <p className="whitespace-pre-wrap mb-2">{message}</p>
            <ul className="list-disc pl-4 space-y-1">
              <li><strong>Provider Error Code:</strong> {code || "Not provided"}</li>
              <li><strong>Param:</strong> {param || "Not provided"}</li>
            </ul>
          </div>
        </div>
        {onDismiss && (
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                type="button"
                onClick={onDismiss}
                className="inline-flex rounded-md bg-red-50 p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 focus:ring-offset-red-50"
              >
                <span className="sr-only">Dismiss</span>
                <svg
                  className="h-3 w-3"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
