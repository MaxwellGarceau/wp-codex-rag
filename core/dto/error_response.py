from typing import ClassVar

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail structure for API responses - matches frontend contract."""

    message: str = Field(
        default="Not provided", description="Human-readable error message"
    )
    statusCode: int = Field(default=500, description="HTTP status code")
    type: str = Field(default="Not provided", description="Error type identifier")
    providerCode: str = Field(default="Not provided", description="Provider error code")

    # Allow additional properties from original errors
    class Config:
        extra: ClassVar[str] = "allow"
        json_schema_extra: ClassVar[dict] = {
            "example": {
                "message": "You exceeded your current quota, please check your plan and billing details.",
                "statusCode": 429,
                "type": "rate_limit",
                "providerCode": "insufficient_quota",
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response structure for all API endpoints."""

    error: ErrorDetail = Field(..., description="Error details")

    class Config:
        json_schema_extra: ClassVar[dict] = {
            "example": {
                "error": {
                    "message": "You exceeded your current quota, please check your plan and billing details.",
                    "statusCode": 429,
                    "type": "rate_limit",
                    "providerCode": "insufficient_quota",
                }
            }
        }
