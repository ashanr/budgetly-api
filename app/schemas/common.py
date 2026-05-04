from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar
from datetime import datetime, timezone
import uuid

T = TypeVar("T")


class Meta(BaseModel):
    request_id: str
    timestamp: str


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    meta: Optional[Meta] = None
    error: Optional[dict] = None

    @classmethod
    def ok(cls, data: Any = None, message: str = "Success", request_id: str = None) -> "APIResponse":
        return cls(
            success=True,
            message=message,
            data=data,
            meta=Meta(
                request_id=request_id or str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            error=None,
        )

    @classmethod
    def fail(cls, message: str, code: str, details: list = None) -> "APIResponse":
        return cls(
            success=False,
            message=message,
            data=None,
            meta=None,
            error={"code": code, "details": details or []},
        )


class PaginatedMeta(Meta):
    page: int
    per_page: int
    total: int
    pages: int
