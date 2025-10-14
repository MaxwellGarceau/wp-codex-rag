"""
Unit tests for core/exceptions/base.py.

This module tests the CustomException class including:
- Exception initialization with custom message
- Default exception properties
- Exception inheritance and behavior
- Message handling and validation
"""

import pytest

from core.exceptions import CustomException


class TestCustomException:
    """Test cases for CustomException class."""

    def test_custom_exception_with_message(self):
        """Test CustomException initialization with custom message."""
        # Given
        message = "Custom error message"

        # When
        exc = CustomException(message=message)

        # Then
        assert exc.message == message
        assert exc.code == 400
        assert exc.error_code == "BAD_GATEWAY"

    def test_custom_exception_without_message(self):
        """Test CustomException initialization without message."""
        # When
        exc = CustomException()

        # Then
        assert exc.message == "BAD GATEWAY"  # Default message
        assert exc.code == 400
        assert exc.error_code == "BAD_GATEWAY"

    def test_custom_exception_with_none_message(self):
        """Test CustomException initialization with None message."""
        # When
        exc = CustomException(message=None)

        # Then
        assert exc.message == "BAD GATEWAY"  # Should use default
        assert exc.code == 400
        assert exc.error_code == "BAD_GATEWAY"

    def test_custom_exception_with_empty_message(self):
        """Test CustomException initialization with empty message."""
        # When
        exc = CustomException(message="")

        # Then
        assert exc.message == ""  # Should use provided empty string
        assert exc.code == 400
        assert exc.error_code == "BAD_GATEWAY"

    def test_custom_exception_inheritance(self):
        """Test that CustomException inherits from Exception."""
        # When
        exc = CustomException("Test message")

        # Then
        assert isinstance(exc, Exception)
        assert isinstance(exc, CustomException)

    def test_custom_exception_default_properties(self):
        """Test CustomException default properties."""
        # When
        exc = CustomException()

        # Then
        assert exc.code == 400
        assert exc.error_code == "BAD_GATEWAY"
        assert exc.message == "BAD GATEWAY"

    def test_custom_exception_can_be_raised(self):
        """Test that CustomException can be raised and caught."""
        # Given
        message = "Test error message"

        # When/Then
        with pytest.raises(CustomException) as exc_info:
            raise CustomException(message=message)

        assert exc_info.value.message == message
        assert exc_info.value.code == 400
        assert exc_info.value.error_code == "BAD_GATEWAY"

    def test_custom_exception_string_representation(self):
        """Test CustomException string representation."""
        # Given
        message = "Test error message"
        exc = CustomException(message=message)

        # When
        str_repr = str(exc)

        # Then
        assert str_repr == message

    def test_custom_exception_with_long_message(self):
        """Test CustomException with long message."""
        # Given
        long_message = (
            "This is a very long error message that contains multiple sentences. " * 10
        )
        exc = CustomException(message=long_message)

        # Then
        assert exc.message == long_message
        assert len(exc.message) > 500

    def test_custom_exception_with_special_characters(self):
        """Test CustomException with special characters in message."""
        # Given
        special_message = "Error with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        exc = CustomException(message=special_message)

        # Then
        assert exc.message == special_message

    def test_custom_exception_with_unicode_characters(self):
        """Test CustomException with unicode characters in message."""
        # Given
        unicode_message = "Error with unicode: 你好世界 🌍 émojis"
        exc = CustomException(message=unicode_message)

        # Then
        assert exc.message == unicode_message

    def test_custom_exception_multiple_instances(self):
        """Test creating multiple CustomException instances."""
        # Given
        message1 = "First error"
        message2 = "Second error"

        # When
        exc1 = CustomException(message=message1)
        exc2 = CustomException(message=message2)

        # Then
        assert exc1.message == message1
        assert exc2.message == message2
        assert exc1 is not exc2
        assert exc1.code == exc2.code  # Same default code
        assert exc1.error_code == exc2.error_code  # Same default error code

    def test_custom_exception_property_access(self):
        """Test accessing CustomException properties."""
        # Given
        exc = CustomException("Test message")

        # Then
        assert hasattr(exc, "message")
        assert hasattr(exc, "code")
        assert hasattr(exc, "error_code")
        assert exc.message == "Test message"
        assert exc.code == 400
        assert exc.error_code == "BAD_GATEWAY"

    def test_custom_exception_immutable_properties(self):
        """Test that CustomException properties can be accessed but are instance-specific."""
        # Given
        exc1 = CustomException("Message 1")
        exc2 = CustomException("Message 2")

        # Then
        # Properties should be instance-specific
        assert exc1.message != exc2.message
        assert exc1.code == exc2.code  # Same default
        assert exc1.error_code == exc2.error_code  # Same default

    def test_custom_exception_in_exception_chain(self):
        """Test CustomException in exception chaining."""
        # Given
        original_exc = ValueError("Original error")
        custom_exc = CustomException("Custom error")

        # When/Then
        with pytest.raises(CustomException):
            try:
                raise original_exc
            except ValueError:
                raise custom_exc

    def test_custom_exception_with_false_message(self):
        """Test CustomException with falsy message values."""
        # Test with False
        exc_false = CustomException(message=False)
        assert exc_false.message == False  # Should use provided value

        # Test with 0
        exc_zero = CustomException(message=0)
        assert exc_zero.message == "BAD GATEWAY"  # Should use default

        # Test with empty list
        exc_empty_list = CustomException(message=[])
        assert exc_empty_list.message == "BAD GATEWAY"  # Should use default
