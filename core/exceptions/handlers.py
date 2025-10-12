"""
Exception handlers for standardized error responses.

This module contains FastAPI exception handlers that provide consistent
error response formatting across the application.
"""
from fastapi import Request
from openai import APIError, RateLimitError

from core.exceptions import CustomException
from core.helpers.error_responses import create_error_response_from_exception


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """

    # Custom exception handler
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return create_error_response_from_exception(
            status_code=exc.code, exception=exc, error_type="custom_error"
        )

    # OpenAI API error handlers
    @app.exception_handler(RateLimitError)
    async def rate_limit_handler(request: Request, exc: RateLimitError):
        return create_error_response_from_exception(
            status_code=429, exception=exc, error_type="rate_limit"
        )

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        return create_error_response_from_exception(
            status_code=500, exception=exc, error_type="api_error"
        )

    # General exception handler for any unhandled exceptions
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return create_error_response_from_exception(
            status_code=500, exception=exc, error_type="internal_error"
        )
