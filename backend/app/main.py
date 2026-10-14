from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.graph.workflow import build_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.app_name = settings.app_name
    app.state.app_version = settings.app_version
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic fulfillment exception investigation and approval workflow.",
    lifespan=lifespan,
)


class ExceptionRequest(BaseModel):
    request_text: str = Field(default="")
    order_id: str = Field(default="")
    user_id: str = Field(default="system")
    user_roles: list[str] = Field(default_factory=list)
    user_permissions: list[str] = Field(default_factory=list)
    approval_decision: str | None = Field(default=None)
    approval_status: str | None = Field(default=None)
    approved_by: str | None = Field(default=None)


def _invoke_workflow(payload: ExceptionRequest) -> dict[str, object]:
    workflow = build_graph()
    thread_id = f"{payload.order_id}-{uuid4().hex[:12]}" if payload.order_id else uuid4().hex[:12]
    result = workflow.invoke(payload.model_dump(exclude_none=True), config={"configurable": {"thread_id": thread_id}})
    return result

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
    }


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "message": f"{settings.app_name} is running.",
        "docs": "/docs",
    }


@app.post("/api/v1/exception/investigate", tags=["exceptions"])
def investigate_exception(payload: ExceptionRequest) -> dict[str, object]:
    return _invoke_workflow(payload)


@app.post("/api/v1/exception/approve", tags=["exceptions"])
def approve_exception(payload: ExceptionRequest) -> dict[str, object]:
    return _invoke_workflow(payload)
