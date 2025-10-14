"""
Unit tests for core/dto/error_response.py.

This module tests the error response DTO models including:
- ErrorDetail model validation and defaults
- ErrorResponse model structure
- JSON schema generation
- Model serialization and deserialization
- Field validation and constraints
"""

import pytest
from pydantic import ValidationError

from core.dto.error_response import ErrorDetail, ErrorResponse


class TestErrorDetail:
    """Test cases for ErrorDetail model."""

    def test_error_detail_defaults(self):
        """Test ErrorDetail model with default values."""
        error_detail = ErrorDetail()

        assert error_detail.message == "Not provided"
        assert error_detail.statusCode == 500
        assert error_detail.type == "Not provided"
        assert error_detail.providerCode == "Not provided"

    def test_error_detail_with_custom_values(self):
        """Test ErrorDetail model with custom values."""
        error_detail = ErrorDetail(
            message="Test error message",
            statusCode=400,
            type="validation_error",
            providerCode="INVALID_INPUT",
        )

        assert error_detail.message == "Test error message"
        assert error_detail.statusCode == 400
        assert error_detail.type == "validation_error"
        assert error_detail.providerCode == "INVALID_INPUT"

    def test_error_detail_field_validation(self):
        """Test ErrorDetail field validation."""
        # Test valid values
        error_detail = ErrorDetail(
            message="Valid message",
            statusCode=200,
            type="success",
            providerCode="SUCCESS",
        )
        assert error_detail.statusCode == 200

        # Test invalid status code type
        with pytest.raises(ValidationError):
            ErrorDetail(statusCode="invalid")

        # Test invalid status code value
        with pytest.raises(ValidationError):
            ErrorDetail(statusCode=-1)

    def test_error_detail_extra_fields_allowed(self):
        """Test that ErrorDetail allows extra fields."""
        error_detail = ErrorDetail(
            message="Test message",
            statusCode=400,
            type="test_error",
            providerCode="TEST_CODE",
            additional_field="additional_value",
            timestamp="2023-01-01T00:00:00Z",
        )

        assert error_detail.message == "Test message"
        assert error_detail.statusCode == 400
        assert error_detail.type == "test_error"
        assert error_detail.providerCode == "TEST_CODE"
        assert error_detail.additional_field == "additional_value"
        assert error_detail.timestamp == "2023-01-01T00:00:00Z"

    def test_error_detail_json_schema(self):
        """Test ErrorDetail JSON schema generation."""
        schema = ErrorDetail.model_json_schema()

        assert "properties" in schema
        assert "message" in schema["properties"]
        assert "statusCode" in schema["properties"]
        assert "type" in schema["properties"]
        assert "providerCode" in schema["properties"]

        # Check field types
        assert schema["properties"]["message"]["type"] == "string"
        assert schema["properties"]["statusCode"]["type"] == "integer"
        assert schema["properties"]["type"]["type"] == "string"
        assert schema["properties"]["providerCode"]["type"] == "string"

        # Check default values
        assert schema["properties"]["message"]["default"] == "Not provided"
        assert schema["properties"]["statusCode"]["default"] == 500
        assert schema["properties"]["type"]["default"] == "Not provided"
        assert schema["properties"]["providerCode"]["default"] == "Not provided"

    def test_error_detail_example_schema(self):
        """Test ErrorDetail example in JSON schema."""
        schema = ErrorDetail.model_json_schema()

        assert "examples" in schema
        example = schema["examples"][0]

        assert (
            example["message"]
            == "You exceeded your current quota, please check your plan and billing details."
        )
        assert example["statusCode"] == 429
        assert example["type"] == "rate_limit"
        assert example["providerCode"] == "insufficient_quota"

    def test_error_detail_serialization(self):
        """Test ErrorDetail model serialization."""
        error_detail = ErrorDetail(
            message="Test message",
            statusCode=400,
            type="test_error",
            providerCode="TEST_CODE",
            additional_field="additional_value",
        )

        # Test model_dump
        data = error_detail.model_dump()
        assert data["message"] == "Test message"
        assert data["statusCode"] == 400
        assert data["type"] == "test_error"
        assert data["providerCode"] == "TEST_CODE"
        assert data["additional_field"] == "additional_value"

        # Test model_dump_json
        json_data = error_detail.model_dump_json()
        assert '"message":"Test message"' in json_data
        assert '"statusCode":400' in json_data
        assert '"type":"test_error"' in json_data
        assert '"providerCode":"TEST_CODE"' in json_data

    def test_error_detail_deserialization(self):
        """Test ErrorDetail model deserialization."""
        data = {
            "message": "Test message",
            "statusCode": 400,
            "type": "test_error",
            "providerCode": "TEST_CODE",
            "additional_field": "additional_value",
        }

        error_detail = ErrorDetail(**data)

        assert error_detail.message == "Test message"
        assert error_detail.statusCode == 400
        assert error_detail.type == "test_error"
        assert error_detail.providerCode == "TEST_CODE"
        assert error_detail.additional_field == "additional_value"

    def test_error_detail_from_dict(self):
        """Test creating ErrorDetail from dictionary."""
        data = {
            "message": "Dict message",
            "statusCode": 422,
            "type": "validation_error",
            "providerCode": "VALIDATION_FAILED",
        }

        error_detail = ErrorDetail.model_validate(data)

        assert error_detail.message == "Dict message"
        assert error_detail.statusCode == 422
        assert error_detail.type == "validation_error"
        assert error_detail.providerCode == "VALIDATION_FAILED"


class TestErrorResponse:
    """Test cases for ErrorResponse model."""

    def test_error_response_creation(self):
        """Test ErrorResponse model creation."""
        error_detail = ErrorDetail(
            message="Test error message",
            statusCode=400,
            type="test_error",
            providerCode="TEST_CODE",
        )

        error_response = ErrorResponse(error=error_detail)

        assert error_response.error == error_detail
        assert error_response.error.message == "Test error message"
        assert error_response.error.statusCode == 400
        assert error_response.error.type == "test_error"
        assert error_response.error.providerCode == "TEST_CODE"

    def test_error_response_creation_with_dict(self):
        """Test ErrorResponse creation with error dictionary."""
        error_data = {
            "message": "Dict error message",
            "statusCode": 500,
            "type": "server_error",
            "providerCode": "SERVER_ERROR",
        }

        error_response = ErrorResponse(error=error_data)

        assert error_response.error.message == "Dict error message"
        assert error_response.error.statusCode == 500
        assert error_response.error.type == "server_error"
        assert error_response.error.providerCode == "SERVER_ERROR"

    def test_error_response_required_error_field(self):
        """Test that ErrorResponse requires error field."""
        with pytest.raises(ValidationError):
            ErrorResponse()

        with pytest.raises(ValidationError):
            ErrorResponse(error=None)

    def test_error_response_json_schema(self):
        """Test ErrorResponse JSON schema generation."""
        schema = ErrorResponse.model_json_schema()

        assert "properties" in schema
        assert "error" in schema["properties"]
        assert "$ref" in schema["properties"]["error"]

        # Check that error field references ErrorDetail
        assert "ErrorDetail" in schema["properties"]["error"]["$ref"]

    def test_error_response_example_schema(self):
        """Test ErrorResponse example in JSON schema."""
        schema = ErrorResponse.model_json_schema()

        assert "examples" in schema
        example = schema["examples"][0]

        assert "error" in example
        assert (
            example["error"]["message"]
            == "You exceeded your current quota, please check your plan and billing details."
        )
        assert example["error"]["statusCode"] == 429
        assert example["error"]["type"] == "rate_limit"
        assert example["error"]["providerCode"] == "insufficient_quota"

    def test_error_response_serialization(self):
        """Test ErrorResponse model serialization."""
        error_detail = ErrorDetail(
            message="Test message",
            statusCode=400,
            type="test_error",
            providerCode="TEST_CODE",
        )

        error_response = ErrorResponse(error=error_detail)

        # Test model_dump
        data = error_response.model_dump()
        assert "error" in data
        assert data["error"]["message"] == "Test message"
        assert data["error"]["statusCode"] == 400
        assert data["error"]["type"] == "test_error"
        assert data["error"]["providerCode"] == "TEST_CODE"

        # Test model_dump_json
        json_data = error_response.model_dump_json()
        assert '"error"' in json_data
        assert '"message":"Test message"' in json_data
        assert '"statusCode":400' in json_data

    def test_error_response_deserialization(self):
        """Test ErrorResponse model deserialization."""
        data = {
            "error": {
                "message": "Test message",
                "statusCode": 400,
                "type": "test_error",
                "providerCode": "TEST_CODE",
            }
        }

        error_response = ErrorResponse(**data)

        assert error_response.error.message == "Test message"
        assert error_response.error.statusCode == 400
        assert error_response.error.type == "test_error"
        assert error_response.error.providerCode == "TEST_CODE"

    def test_error_response_from_dict(self):
        """Test creating ErrorResponse from dictionary."""
        data = {
            "error": {
                "message": "Dict message",
                "statusCode": 422,
                "type": "validation_error",
                "providerCode": "VALIDATION_FAILED",
            }
        }

        error_response = ErrorResponse.model_validate(data)

        assert error_response.error.message == "Dict message"
        assert error_response.error.statusCode == 422
        assert error_response.error.type == "validation_error"
        assert error_response.error.providerCode == "VALIDATION_FAILED"


class TestErrorResponseIntegration:
    """Integration tests for error response models."""

    def test_error_response_roundtrip_serialization(self):
        """Test complete roundtrip serialization and deserialization."""
        # Create original error response
        original_error = ErrorDetail(
            message="Original message",
            statusCode=400,
            type="original_error",
            providerCode="ORIGINAL_CODE",
            additional_field="additional_value",
        )
        original_response = ErrorResponse(error=original_error)

        # Serialize to JSON
        json_data = original_response.model_dump_json()

        # Deserialize from JSON
        deserialized_response = ErrorResponse.model_validate_json(json_data)

        # Should match original
        assert deserialized_response.error.message == original_error.message
        assert deserialized_response.error.statusCode == original_error.statusCode
        assert deserialized_response.error.type == original_error.type
        assert deserialized_response.error.providerCode == original_error.providerCode
        assert (
            deserialized_response.error.additional_field
            == original_error.additional_field
        )

    def test_error_response_with_complex_data(self):
        """Test ErrorResponse with complex nested data."""
        error_detail = ErrorDetail(
            message="Complex error",
            statusCode=400,
            type="complex_error",
            providerCode="COMPLEX_CODE",
            metadata={
                "user_id": 123,
                "request_id": "req-456",
                "timestamp": "2023-01-01T00:00:00Z",
            },
            validation_errors=[
                {"field": "email", "message": "Invalid email format"},
                {"field": "password", "message": "Password too short"},
            ],
        )

        error_response = ErrorResponse(error=error_detail)

        # Should handle complex data
        assert error_response.error.metadata["user_id"] == 123
        assert error_response.error.metadata["request_id"] == "req-456"
        assert len(error_response.error.validation_errors) == 2
        assert error_response.error.validation_errors[0]["field"] == "email"

    def test_error_response_consistency_with_helpers(self):
        """Test that ErrorResponse works consistently with helper functions."""
        from core.helpers.error_responses import create_error_response

        # Create error response using helper
        helper_response = create_error_response(
            status_code=400,
            message="Helper message",
            error_type="helper_error",
            providerCode="HELPER_CODE",
        )

        # Extract content
        import json

        content = json.loads(helper_response.body.decode("utf-8"))

        # Should be able to create ErrorResponse from helper output
        error_response = ErrorResponse(**content)

        assert error_response.error.message == "Helper message"
        assert error_response.error.statusCode == 400
        assert error_response.error.type == "helper_error"
        assert error_response.error.providerCode == "HELPER_CODE"

    def test_error_response_field_descriptions(self):
        """Test that ErrorResponse fields have proper descriptions."""
        schema = ErrorResponse.model_json_schema()

        # Check that error field has description
        assert "description" in schema["properties"]["error"]
        assert "Error details" in schema["properties"]["error"]["description"]

    def test_error_detail_field_descriptions(self):
        """Test that ErrorDetail fields have proper descriptions."""
        schema = ErrorDetail.model_json_schema()

        # Check field descriptions
        assert "description" in schema["properties"]["message"]
        assert (
            "Human-readable error message"
            in schema["properties"]["message"]["description"]
        )

        assert "description" in schema["properties"]["statusCode"]
        assert "HTTP status code" in schema["properties"]["statusCode"]["description"]

        assert "description" in schema["properties"]["type"]
        assert "Error type identifier" in schema["properties"]["type"]["description"]

        assert "description" in schema["properties"]["providerCode"]
        assert (
            "Provider error code" in schema["properties"]["providerCode"]["description"]
        )
