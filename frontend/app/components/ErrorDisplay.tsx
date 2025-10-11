interface ErrorDisplayProps {
  error: string;
  onDismiss?: () => void;
}

export function ErrorDisplay({ error, onDismiss }: ErrorDisplayProps) {
  const formatErrorMessage = (error: string): { statusCode?: string; errorCode?: string; message: string } => {
    // Try to parse as JSON first (structured error response)
    try {
      const errorData = JSON.parse(error);
      if (errorData.error) {
        const { message, type, code } = errorData.error;
        return {
          statusCode: "Unknown",
          errorCode: code || type || "unknown",
          message: message || "An error occurred"
        };
      }
    } catch {
      // Not JSON, try to extract from error message format
    }

    // Try to extract status code and error code from error message
    // Look for patterns like "Error code: 429 - insufficient_quota" or "HTTP 500: Internal Server Error"
    const statusCodeMatch = error.match(/(?:HTTP\s+)?(\d{3})/);
    const errorCodeMatch = error.match(/(?:Error code:\s*\d+\s*-\s*)?([a-zA-Z_]+)/);
    
    // Extract the main error message (everything after the first colon or dash)
    const messageMatch = error.match(/(?:Error code:\s*\d+\s*-\s*[a-zA-Z_]+\s*)?(.*)/);
    
    return {
      statusCode: statusCodeMatch ? statusCodeMatch[1] : undefined,
      errorCode: errorCodeMatch ? errorCodeMatch[1] : undefined,
      message: messageMatch ? messageMatch[1].trim() : error
    };
  };

  const { statusCode, errorCode, message } = formatErrorMessage(error);

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
            {statusCode && errorCode && (
              <p className="font-mono font-medium mb-1">
                Error code: {statusCode} - {errorCode}
              </p>
            )}
            <p className="whitespace-pre-wrap">{message}</p>
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
