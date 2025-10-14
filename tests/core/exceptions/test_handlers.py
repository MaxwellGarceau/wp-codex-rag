"""
Unit tests for core/exceptions/handlers.py.

This module tests the exception handler registration functionality including:
- register_exception_handlers function
- Custom exception handler
- OpenAI API error handlers
- General exception handler
- Handler registration with FastAPI app
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, Request
from openai import APIError, RateLimitError

from core.exceptions import CustomException
from core.exceptions.handlers import register_exception_handlers


class TestRegisterExceptionHandlers:
    """Test cases for register_exception_handlers function."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.app = FastAPI()
        self.request = Mock(spec=Request)

    def test_register_exception_handlers_registers_all_handlers(self):
        """Test that register_exception_handlers registers all expected handlers."""
        with patch(
            "core.exceptions.handlers.create_error_response_from_exception"
        ) as mock_create_response:
            mock_create_response.return_value = Mock()

            # Register handlers
            register_exception_handlers(self.app)

            # Check that exception handlers were registered
            assert len(self.app.exception_handlers) >= 4

            # Check for specific exception types
            exception_types = [
                handler_type for handler_type in self.app.exception_handlers.keys()
            ]
            assert CustomException in exception_types
            assert RateLimitError in exception_types
            assert APIError in exception_types
            assert Exception in exception_types

    def test_custom_exception_handler(self):
        """Test custom exception handler."""
        with patch(
            "core.exceptions.handlers.create_error_response_from_exception"
        ) as mock_create_response:
            mock_response = Mock()
            mock_create_response.return_value = mock_response

            # Register handlers
            register_exception_handlers(self.app)

            # Create custom exception
            custom_exc = CustomException("Custom error message")
            custom_exc.code = 400

            # Get the handler
            handler = self.app.exception_handlers[CustomException]

            # Test the handler
            result = handler(self.request, custom_exc)

            # Verify create_error_response_from_exception was called correctly
            mock_create_response.assert_called_once_with(
                status_code=400, exception=custom_exc, error_type="custom_error"
            )
            assert result == mock_response

    def test_custom_exception_handler_with_default_code(self):
        """Test custom exception handler with default code."""
        with patch(
            "core.exceptions.handlers.create_error_response_from_exception"
        ) as mock_create_response:
            mock_response = Mock()
            mock_create_response.return_value = mock_response

            # Register handlers
            register_exception_handlers(self.app)

            # Create custom exception without setting code
            custom_exc = CustomException("Custom error message")
            # Don't set code, should use default

            # Get the handler
            handler = self.app.exception_handlers[CustomException]

            # Test the handler
            result = handler(self.request, custom_exc)

            # Verify create_error_response_from_exception was called with default code
            mock_create_response.assert_called_once_with(
                status_code=400,  # Default code from CustomException
                exception=custom_exc,
                error_type="custom_error",
            )
            assert result == mock_response

    def test_rate_limit_handler(self):
        """Test rate limit error handler."""
        with patch(
            "core.exceptions.handlers.create_error_response_from_exception"
        ) as mock_create_response:
            mock_response = Mock()
            mock_create_response.return_value = mock_response

            # Register handlers
            register_exception_handlers(self.app)

            # Create rate limit error
            rate_limit_exc = RateLimitError("Rate limit exceeded")

            # Get the handler
            handler = self.app.exception_handlers[RateLimitError]

            # Test the handler
            result = handler(self.request, rate_limit_exc)

            # Verify create_error_response_from_exception was called correctly
            mock_create_response.assert_called_once_with(
                status_code=429, exception=rate_limit_exc, error_type="rate_limit"
            )
            assert result == mock_response

    def test_api_error_handler(self):
        """Test API error handler."""
        with patch(
            "core.exceptions.handlers.create_error_response_from_exception"
        ) as mock_create_response:
            mock_response = Mock()
            mock_create_response.return_value = mock_response

            # Register handlers
            register_exception_handlers(self.app)

            # Create API error
            api_exc = APIError("API error occurred")

            # Get the handler
            handler = self.app.exception_handlers[APIError]

            # Test the handler
            result = handler(self.request, api_exc)

            # Verify create_error_response_from_exception was called correctly
            mock_create_response.assert_called_once_with(
                status_code=500, exception=api_exc, error_type="api_error"
            )
            assert result == mock_response

    def test_general_exception_handler(self):
        """Test general exception handler."""
        with patch(
            "core.exceptions.handlers.create_error_response_from_exception"
        ) as mock_create_response:
            mock_response = Mock()
            mock_create_response.return_value = mock_response

            # Register handlers
            register_exception_handlers(self.app)

            # Create general exception
            general_exc = ValueError("General error occurred")

            # Get the handler
            handler = self.app.exception_handlers[Exception]

            # Test the handler
            result = handler(self.request, general_exc)

            # Verify create_error_response_from_exception was called correctly
            mock_create_response.assert_called_once_with(
                status_code=500, exception=general_exc, error_type="internal_error"
            )
            assert result == mock_response

    def test_exception_handler_async_behavior(self):
        """Test that exception handlers are async functions."""
        register_exception_handlers(self.app)

        # All handlers should be async
        for handler in self.app.exception_handlers.values():
            assert hasattr(handler, "__code__")
            # Check if it's a coroutine function
            import inspect

            assert inspect.iscoroutinefunction(handler)

    def test_exception_handler_request_parameter(self):
        """Test that exception handlers receive request parameter."""
        with patch(
            "core.exceptions.handlers.create_error_response_from_exception"
        ) as mock_create_response:
            mock_response = Mock()
            mock_create_response.return_value = mock_response

            register_exception_handlers(self.app)

            # Create exception
            exc = CustomException("Test error")

            # Get the handler
            handler = self.app.exception_handlers[CustomException]

            # Test that handler can be called with request and exception
            result = handler(self.request, exc)

            # Should not raise any errors
            assert result == mock_response

    def test_exception_handler_error_creation_failure(self):
        """Test exception handler behavior when error response creation fails."""
        with patch(
            "core.exceptions.handlers.create_error_response_from_exception"
        ) as mock_create_response:
            # Make create_error_response_from_exception raise an exception
            mock_create_response.side_effect = Exception("Error creation failed")

            register_exception_handlers(self.app)

            # Create exception
            exc = CustomException("Test error")

            # Get the handler
            handler = self.app.exception_handlers[CustomException]

            # Test that handler raises the exception from create_error_response_from_exception
            with pytest.raises(Exception, match="Error creation failed"):
                handler(self.request, exc)

    def test_multiple_exception_handlers_registration(self):
        """Test that multiple calls to register_exception_handlers don't cause issues."""
        with patch(
            "core.exceptions.handlers.create_error_response_from_exception"
        ) as mock_create_response:
            mock_create_response.return_value = Mock()

            # Register handlers multiple times
            register_exception_handlers(self.app)
            initial_handler_count = len(self.app.exception_handlers)

            register_exception_handlers(self.app)

            # Should not duplicate handlers
            assert len(self.app.exception_handlers) == initial_handler_count

    def test_exception_handler_with_different_exception_types(self):
        """Test exception handlers with various exception types."""
        with patch(
            "core.exceptions.handlers.create_error_response_from_exception"
        ) as mock_create_response:
            mock_response = Mock()
            mock_create_response.return_value = mock_response

            register_exception_handlers(self.app)

            # Test different exception types
            exceptions_to_test = [
                (CustomException("Custom error"), 400, "custom_error"),
                (RateLimitError("Rate limit"), 429, "rate_limit"),
                (APIError("API error"), 500, "api_error"),
                (ValueError("Value error"), 500, "internal_error"),
                (RuntimeError("Runtime error"), 500, "internal_error"),
            ]

            for exc, expected_status, expected_type in exceptions_to_test:
                # Find the appropriate handler
                handler = None
                for exc_type, handler_func in self.app.exception_handlers.items():
                    if isinstance(exc, exc_type):
                        handler = handler_func
                        break

                assert handler is not None, f"No handler found for {type(exc)}"

                # Test the handler
                result = handler(self.request, exc)

                # Verify create_error_response_from_exception was called correctly
                mock_create_response.assert_called_with(
                    status_code=expected_status, exception=exc, error_type=expected_type
                )
                assert result == mock_response

                # Reset mock for next iteration
                mock_create_response.reset_mock()

    def test_exception_handler_integration_with_fastapi(self):
        """Test exception handlers integration with FastAPI app."""
        app = FastAPI()

        # Register handlers
        register_exception_handlers(app)

        # Create a test endpoint that raises an exception
        @app.get("/test-custom-exception")
        async def test_custom_exception():
            raise CustomException("Test custom exception")

        @app.get("/test-rate-limit")
        async def test_rate_limit():
            raise RateLimitError("Test rate limit")

        @app.get("/test-api-error")
        async def test_api_error():
            raise APIError("Test API error")

        @app.get("/test-general-exception")
        async def test_general_exception():
            raise ValueError("Test general exception")

        # Test that handlers are properly registered
        assert CustomException in app.exception_handlers
        assert RateLimitError in app.exception_handlers
        assert APIError in app.exception_handlers
        assert Exception in app.exception_handlers

        # Test that handlers are callable
        for handler in app.exception_handlers.values():
            assert callable(handler)

    def test_exception_handler_with_mocked_request(self):
        """Test exception handlers with properly mocked request object."""
        with patch(
            "core.exceptions.handlers.create_error_response_from_exception"
        ) as mock_create_response:
            mock_response = Mock()
            mock_create_response.return_value = mock_response

            register_exception_handlers(self.app)

            # Create a more realistic request mock
            request = Mock(spec=Request)
            request.url = Mock()
            request.url.path = "/test/path"
            request.method = "GET"
            request.headers = {"content-type": "application/json"}

            # Create exception
            exc = CustomException("Test error")

            # Get the handler
            handler = self.app.exception_handlers[CustomException]

            # Test the handler
            result = handler(request, exc)

            # Should work without issues
            assert result == mock_response
            mock_create_response.assert_called_once_with(
                status_code=400, exception=exc, error_type="custom_error"
            )
