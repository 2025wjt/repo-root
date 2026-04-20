from typing import Any

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Any = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
