from typing import Generic, TypeVar, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    ok: bool = True
    data: list[T] = Field(default_factory=list)
    row_count: int = 0
    cached: bool = False
    cached_at: Optional[datetime] = None
    pg_version: int = 0
    execution_ms: int = 0

class APIErrorResponse(BaseModel):
    ok: bool = False
    error: str
    suggestion: Optional[str] = None
