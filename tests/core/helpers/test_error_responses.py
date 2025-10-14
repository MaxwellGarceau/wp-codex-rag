"""
Unit tests for core/helpers/error_responses.py.

This module tests the error response creation functionality including:
- create_error_response_from_exception function
- create_error_response function
- create_http_exception function
- Error response formatting and structure
- Exception property extraction
"""

import json
from unittest.mock import Mock

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from core.dto.error_response import ErrorResponse
from core.helpers.error_responses import (
    create_error_response,
    create_error_response_from_exception,
    create_http_exception,
)


class TestCreateErrorResponseFromException:
    """Test cases for create_error_response_from_exception function."""

    def test_create_error_response_from_exception_basic(self):
        """Test basic error response creation from exception."""
        exception = Exception("Test error message")
        response = create_error_response_from_exception(
            status_code=400, exception=exception, error_type="test_error"
        )

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert "error" in error_data
        assert error_data["error"]["message"] == "Test error message"
        assert error_data["error"]["statusCode"] == 400
        assert error_data["error"]["type"] == "test_error"
        assert error_data["error"]["providerCode"] == "Not provided"

    def test_create_error_response_from_exception_with_custom_message(self):
        """Test error response creation with custom exception message."""
        exception = Exception("Custom error message")
        response = create_error_response_from_exception(
            status_code=500, exception=exception, error_type="custom_error"
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["message"] == "Custom error message"
        assert error_data["error"]["statusCode"] == 500
        assert error_data["error"]["type"] == "custom_error"

    def test_create_error_response_from_exception_with_body_message(self):
        """Test error response creation from exception with body.message."""
        exception = Mock()
        exception.body = {"message": "Body error message"}
        exception.code = "BODY_ERROR"

        response = create_error_response_from_exception(
            status_code=422, exception=exception, error_type="body_error"
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["message"] == "Body error message"
        assert error_data["error"]["providerCode"] == "BODY_ERROR"

    def test_create_error_response_from_exception_with_exception_message_attribute(
        self,
    ):
        """Test error response creation from exception with message attribute."""
        exception = Mock()
        exception.message = "Attribute error message"
        exception.code = "ATTR_ERROR"

        response = create_error_response_from_exception(
            status_code=403, exception=exception, error_type="attribute_error"
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["message"] == "Attribute error message"
        assert error_data["error"]["providerCode"] == "ATTR_ERROR"

    def test_create_error_response_from_exception_with_additional_properties(self):
        """Test error response creation with additional exception properties."""
        exception = Mock()
        exception.message = "Test message"
        exception.code = "TEST_CODE"
        exception.details = "Additional details"
        exception.timestamp = "2023-01-01T00:00:00Z"
        exception._private_attr = "Should be ignored"

        response = create_error_response_from_exception(
            status_code=400, exception=exception, error_type="test_error"
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["message"] == "Test message"
        assert error_data["error"]["providerCode"] == "TEST_CODE"
        assert error_data["error"]["details"] == "Additional details"
        assert error_data["error"]["timestamp"] == "2023-01-01T00:00:00Z"
        assert "_private_attr" not in error_data["error"]

    def test_create_error_response_from_exception_with_non_serializable_properties(
        self,
    ):
        """Test error response creation with non-JSON serializable properties."""
        exception = Mock()
        exception.message = "Test message"
        exception.code = "TEST_CODE"
        exception.complex_object = Mock()  # Non-serializable
        exception.simple_list = [1, 2, 3]  # Serializable

        response = create_error_response_from_exception(
            status_code=400, exception=exception, error_type="test_error"
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["message"] == "Test message"
        assert error_data["error"]["providerCode"] == "TEST_CODE"
        assert error_data["error"]["simple_list"] == [1, 2, 3]
        # Complex object should be converted to string
        assert "complex_object" in error_data["error"]

    def test_create_error_response_from_exception_empty_message(self):
        """Test error response creation with empty exception message."""
        exception = Exception("")
        response = create_error_response_from_exception(
            status_code=400, exception=exception, error_type="empty_error"
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        # Empty string evaluates to False, so it falls back to "Not provided"
        assert error_data["error"]["message"] == "Not provided"

    def test_create_error_response_from_exception_none_code(self):
        """Test error response creation with None code."""
        exception = Mock()
        exception.message = "Test message"
        exception.code = None

        response = create_error_response_from_exception(
            status_code=400, exception=exception, error_type="none_code_error"
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["providerCode"] == "Not provided"

    def test_create_error_response_from_exception_default_error_type(self):
        """Test error response creation with default error type."""
        exception = Exception("Test message")
        response = create_error_response_from_exception(
            status_code=400, exception=exception
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["type"] == "Not provided"


class TestCreateErrorResponse:
    """Test cases for create_error_response function."""

    def test_create_error_response_basic(self):
        """Test basic error response creation."""
        response = create_error_response(
            status_code=400, message="Test error message", error_type="test_error"
        )

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["message"] == "Test error message"
        assert error_data["error"]["statusCode"] == 400
        assert error_data["error"]["type"] == "test_error"
        assert error_data["error"]["providerCode"] == "test_error"

    def test_create_error_response_with_provider_code(self):
        """Test error response creation with custom provider code."""
        response = create_error_response(
            status_code=429,
            message="Rate limit exceeded",
            error_type="rate_limit",
            providerCode="RATE_LIMIT_EXCEEDED",
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["message"] == "Rate limit exceeded"
        assert error_data["error"]["statusCode"] == 429
        assert error_data["error"]["type"] == "rate_limit"
        assert error_data["error"]["providerCode"] == "RATE_LIMIT_EXCEEDED"

    def test_create_error_response_with_additional_properties(self):
        """Test error response creation with additional properties."""
        response = create_error_response(
            status_code=400,
            message="Validation error",
            error_type="validation_error",
            providerCode="INVALID_INPUT",
            field="email",
            value="invalid-email",
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["message"] == "Validation error"
        assert error_data["error"]["field"] == "email"
        assert error_data["error"]["value"] == "invalid-email"

    def test_create_error_response_with_none_values(self):
        """Test error response creation with None values."""
        response = create_error_response(
            status_code=500, message=None, error_type=None, providerCode=None
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["message"] == "Not provided"
        assert error_data["error"]["type"] == "Not provided"
        assert error_data["error"]["providerCode"] == "Not provided"

    def test_create_error_response_with_empty_strings(self):
        """Test error response creation with empty strings."""
        response = create_error_response(
            status_code=400, message="", error_type="", providerCode=""
        )

        content = response.body.decode("utf-8")
        error_data = json.loads(content)

        assert error_data["error"]["message"] == "Not provided"
        assert error_data["error"]["type"] == "Not provided"
        assert error_data["error"]["providerCode"] == "Not provided"


class TestCreateHttpException:
    """Test cases for create_http_exception function."""

    def test_create_http_exception_basic(self):
        """Test basic HTTP exception creation."""
        exception = create_http_exception(
            status_code=400, message="Test error message", error_type="test_error"
        )

        assert isinstance(exception, HTTPException)
        assert exception.status_code == 400

        detail = exception.detail
        assert "error" in detail
        assert detail["error"]["message"] == "Test error message"
        assert detail["error"]["statusCode"] == 400
        assert detail["error"]["type"] == "test_error"
        assert detail["error"]["providerCode"] == "test_error"

    def test_create_http_exception_with_provider_code(self):
        """Test HTTP exception creation with custom provider code."""
        exception = create_http_exception(
            status_code=403,
            message="Access denied",
            error_type="access_denied",
            providerCode="ACCESS_DENIED",
        )

        detail = exception.detail
        assert detail["error"]["message"] == "Access denied"
        assert detail["error"]["statusCode"] == 403
        assert detail["error"]["type"] == "access_denied"
        assert detail["error"]["providerCode"] == "ACCESS_DENIED"

    def test_create_http_exception_with_additional_properties(self):
        """Test HTTP exception creation with additional properties."""
        exception = create_http_exception(
            status_code=422,
            message="Validation failed",
            error_type="validation_error",
            providerCode="VALIDATION_FAILED",
            field="username",
            constraint="min_length",
        )

        detail = exception.detail
        assert detail["error"]["message"] == "Validation failed"
        assert detail["error"]["field"] == "username"
        assert detail["error"]["constraint"] == "min_length"

    def test_create_http_exception_with_none_values(self):
        """Test HTTP exception creation with None values."""
        exception = create_http_exception(
            status_code=500, message=None, error_type=None, providerCode=None
        )

        detail = exception.detail
        assert detail["error"]["message"] == "Not provided"
        assert detail["error"]["type"] == "Not provided"
        assert detail["error"]["providerCode"] == "Not provided"

    def test_create_http_exception_consistency_with_error_response(self):
        """Test that HTTP exception detail matches error response structure."""
        # Create both types of responses
        error_response = create_error_response(
            status_code=400,
            message="Test message",
            error_type="test_error",
            providerCode="TEST_CODE",
        )

        http_exception = create_http_exception(
            status_code=400,
            message="Test message",
            error_type="test_error",
            providerCode="TEST_CODE",
        )

        # Extract content from both
        error_content = json.loads(error_response.body.decode("utf-8"))
        http_detail = http_exception.detail

        # Should have the same structure
        assert error_content == http_detail


class TestErrorResponseIntegration:
    """Integration tests for error response system."""

    def test_error_response_structure_consistency(self):
        """Test that all error response functions produce consistent structure."""
        # Test data
        status_code = 400
        message = "Test error"
        error_type = "test_error"
        provider_code = "TEST_CODE"

        # Create responses using different functions
        response1 = create_error_response(
            status_code=status_code,
            message=message,
            error_type=error_type,
            providerCode=provider_code,
        )

        exception = Mock()
        exception.message = message
        exception.code = provider_code
        response2 = create_error_response_from_exception(
            status_code=status_code, exception=exception, error_type=error_type
        )

        http_exception = create_http_exception(
            status_code=status_code,
            message=message,
            error_type=error_type,
            providerCode=provider_code,
        )

        # Extract content
        content1 = json.loads(response1.body.decode("utf-8"))
        content2 = json.loads(response2.body.decode("utf-8"))
        detail3 = http_exception.detail

        # All should have the same error structure
        assert content1["error"]["message"] == content2["error"]["message"]
        assert content1["error"]["message"] == detail3["error"]["message"]
        assert content1["error"]["statusCode"] == content2["error"]["statusCode"]
        assert content1["error"]["statusCode"] == detail3["error"]["statusCode"]
        assert content1["error"]["type"] == content2["error"]["type"]
        assert content1["error"]["type"] == detail3["error"]["type"]

    def test_error_response_validation(self):
        """Test that error responses can be validated against ErrorResponse model."""
        response = create_error_response(
            status_code=400,
            message="Test message",
            error_type="test_error",
            providerCode="TEST_CODE",
        )

        content = json.loads(response.body.decode("utf-8"))

        # Should be able to create ErrorResponse from the content
        error_response = ErrorResponse(**content)
        assert error_response.error.message == "Test message"
        assert error_response.error.statusCode == 400
        assert error_response.error.type == "test_error"
        assert error_response.error.providerCode == "TEST_CODE"

    def test_error_response_json_serialization(self):
        """Test that error responses are properly JSON serializable."""
        response = create_error_response(
            status_code=400,
            message="Test message",
            error_type="test_error",
            providerCode="TEST_CODE",
            additional_field="additional_value",
        )

        content = json.loads(response.body.decode("utf-8"))

        # Should be able to serialize and deserialize
        serialized = json.dumps(content)
        deserialized = json.loads(serialized)

        assert deserialized == content
        assert deserialized["error"]["message"] == "Test message"
        assert deserialized["error"]["additional_field"] == "additional_value"
