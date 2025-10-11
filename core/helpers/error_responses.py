import json
from typing import Optional, Any, Dict

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from core.dto.error_response import ErrorResponse


def create_error_response_from_exception(
    status_code: int,
    exception: Exception,
    error_type: str = "Not provided"
) -> JSONResponse:
    """
    Create a standardized error response from an exception, preserving original properties.
    
    Args:
        status_code: HTTP status code
        exception: The original exception
        error_type: Error type identifier (defaults to "Not provided")
        
    Returns:
        JSONResponse with standardized error format preserving original properties
    """
    # Extract properties from the original exception
    # For OpenAI exceptions, try to get the clean message from the exception's body.message
    # Otherwise fall back to str(exception)
    clean_message = "Not provided"
    if hasattr(exception, 'body') and isinstance(exception.body, dict) and 'message' in exception.body:
        clean_message = str(exception.body['message'])
    elif hasattr(exception, 'message') and exception.message:
        clean_message = str(exception.message)
    elif str(exception):
        clean_message = str(exception)
    
    error_data = {
        "message": clean_message,
        "statusCode": status_code,
        "type": error_type,
        "providerCode": getattr(exception, 'code', "Not provided") or "Not provided"
    }
    
    # Add any additional properties from the original exception that are JSON serializable
    if hasattr(exception, '__dict__'):
        for key, value in exception.__dict__.items():
            if key not in error_data and not key.startswith('_'):
                # Only include JSON serializable values
                try:
                    json.dumps(value)  # Test if it's JSON serializable
                    error_data[key] = value
                except (TypeError, ValueError):
                    # Convert non-serializable objects to strings
                    error_data[key] = str(value)
    
    error_response = ErrorResponse(error=error_data)
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(),
    )


def create_error_response(
    status_code: int,
    message: str,
    error_type: str,
    param: Optional[str] = None,
    code: Optional[str] = None,
    **additional_properties
) -> JSONResponse:
    """
    Create a standardized error response with fallbacks.
    
    Args:
        status_code: HTTP status code
        message: Human-readable error message
        error_type: Error type identifier
        param: Parameter that caused the error (optional)
        code: Error code (optional)
        **additional_properties: Additional properties to include
        
    Returns:
        JSONResponse with standardized error format
    """
    error_data = {
        "message": message or "Not provided",
        "statusCode": status_code,
        "type": error_type or "Not provided",
        "providerCode": code or error_type or "Not provided"
    }
    
    # Add any additional properties
    error_data.update(additional_properties)
    
    error_response = ErrorResponse(error=error_data)
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(),
    )


def create_http_exception(
    status_code: int,
    message: str,
    error_type: str,
    param: Optional[str] = None,
    code: Optional[str] = None,
    **additional_properties
) -> HTTPException:
    """
    Create a standardized HTTP exception with fallbacks.
    
    Args:
        status_code: HTTP status code
        message: Human-readable error message
        error_type: Error type identifier
        param: Parameter that caused the error (optional)
        code: Error code (optional)
        **additional_properties: Additional properties to include
        
    Returns:
        HTTPException with standardized error format
    """
    error_data = {
        "message": message or "Not provided",
        "statusCode": status_code,
        "type": error_type or "Not provided",
        "providerCode": code or error_type or "Not provided"
    }
    
    # Add any additional properties
    error_data.update(additional_properties)
    
    error_response = ErrorResponse(error=error_data)
    
    return HTTPException(
        status_code=status_code,
        detail=error_response.model_dump(),
    )
