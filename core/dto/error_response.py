from typing import Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail structure for API responses."""
    
    message: str = Field(..., description="Human-readable error message")
    type: str = Field(..., description="Error type identifier")
    param: Optional[str] = Field(None, description="Parameter that caused the error")
    code: Optional[str] = Field(None, description="Error code")


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
