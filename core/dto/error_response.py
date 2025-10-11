from typing import Optional, Any, Dict

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail structure for API responses - preserves original error properties."""
    
    message: str = Field(default="Not provided", description="Human-readable error message")
    type: str = Field(default="Not provided", description="Error type identifier")
    param: Optional[str] = Field(default="Not provided", description="Parameter that caused the error")
    code: Optional[str] = Field(default="Not provided", description="Error code")
    
    # Allow additional properties from original errors
    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "message": "You exceeded your current quota, please check your plan and billing details.",
                "type": "insufficient_quota",
                "param": None,
                "code": "insufficient_quota"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response structure for all API endpoints."""
    
    error: ErrorDetail = Field(..., description="Error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "message": "You exceeded your current quota, please check your plan and billing details.",
                    "type": "insufficient_quota",
                    "param": None,
                    "code": "insufficient_quota"
                }
            }
        }
