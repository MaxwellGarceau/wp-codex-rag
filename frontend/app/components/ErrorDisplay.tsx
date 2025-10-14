import { ErrorProperties } from "../services/ragClient";
import { useEffect, useState } from "react";

interface ErrorDisplayProps {
  error: string; // Can be JSON string of ErrorProperties or plain error message
  onDismiss?: () => void;
}

// NOTE: Frontend relies on the BE contract for the error response
export function ErrorDisplay({ error, onDismiss }: ErrorDisplayProps) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const parseError = (error: string): ErrorProperties => {
    try {
      const parsed = JSON.parse(error) as ErrorProperties;

      // Ensure required properties exist with fallbacks
      return {
        message: parsed.message || "Unknown error",
        statusCode: parsed.statusCode || "Not provided",
        type: parsed.type || "unknown",
        providerCode: parsed.providerCode || "Not provided"
      };
    } catch {
      // Fallback for non-JSON errors
      return {
        message: error,
        statusCode: "Not provided",
        type: "Not provided",
        providerCode: "Not provided"
      };
    }
  };

  // Prevent hydration mismatch by not rendering until client-side
  if (!isClient) {
    return null;
  }

  const { statusCode, type, message, providerCode } = parseError(error);

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
            {statusCode && type && (
              <p className="font-mono font-medium mb-2">
                Error code: {statusCode} - {type}
              </p>
            )}
            <p className="whitespace-pre-wrap mb-2">{message}</p>
            <ul className="list-disc pl-4 space-y-1">
              <li><strong>Provider Error Code:</strong> {providerCode || "Not provided"}</li>
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
