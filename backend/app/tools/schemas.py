from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AuthContext(BaseModel):
    user_id: str
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class ToolResult(BaseModel):
    is_success: bool
    data: Any = None
    error: str | None = None
    trace_id: str = Field(default_factory=lambda: uuid4().hex[:12])
    warnings: list[str] = Field(default_factory=list)
