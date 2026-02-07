"""Standard API responses"""
from pydantic import BaseModel
from typing import Optional, Any


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class ExplanationResponse(BaseModel):
    explanation: str
