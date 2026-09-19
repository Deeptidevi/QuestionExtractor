from typing import Generic, List, Optional, TypeVar, Any, Dict
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Unique error identifier code")
    message: str = Field(..., description="Human-readable error explanation")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class ErrorResponse(BaseModel):
    error: ErrorDetail


class PaginationMeta(BaseModel):
    page: int = Field(1, ge=1, description="Current page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a subsequent page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginationMeta


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
