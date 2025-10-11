from typing import Optional

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from core.dto.error_response import ErrorResponse


def create_error_response(
    status_code: int,
    message: str,
    error_type: str,
    param: Optional[str] = None,
    code: Optional[str] = None
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        message: Human-readable error message
        error_type: Error type identifier
        param: Parameter that caused the error (optional)
        code: Error code (optional)
        
    Returns:
        JSONResponse with standardized error format
    """
    error_response = ErrorResponse(
        error={
            "message": message,
            "type": error_type,
            "param": param,
            "code": code or error_type
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(),
    )


def create_http_exception(
    status_code: int,
    message: str,
    error_type: str,
    param: Optional[str] = None,
    code: Optional[str] = None
) -> HTTPException:
    """
    Create a standardized HTTP exception.
    
    Args:
        status_code: HTTP status code
        message: Human-readable error message
        error_type: Error type identifier
        param: Parameter that caused the error (optional)
        code: Error code (optional)
        
    Returns:
        HTTPException with standardized error format
    """
    error_response = ErrorResponse(
        error={
            "message": message,
            "type": error_type,
            "param": param,
            "code": code or error_type
        }
    )
    
    return HTTPException(
        status_code=status_code,
        detail=error_response.model_dump(),
    )
