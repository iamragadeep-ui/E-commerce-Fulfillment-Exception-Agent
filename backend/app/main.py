
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.app.agents.workflow import run_investigation
from backend.app.guardrails.rules import validate_exception

app = FastAPI(title="E-commerce Fulfillment Exception Agent")


class FulfillmentExceptionRequest(BaseModel):
    order_id: str = Field(min_length=1)
    issue_description: str = Field(min_length=5)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "fulfillment-exception-agent",
    }


@app.post("/exceptions")
def create_exception(request: FulfillmentExceptionRequest):
    validation = validate_exception(
        request.order_id,
        request.issue_description,
    )

    if not validation["allowed"]:
        raise HTTPException(
            status_code=400,
            detail=validation["reason"],
        )

    result = run_investigation(
        order_id=request.order_id,
        issue_description=request.issue_description,
    )

    return {
        "message": "Fulfillment investigation completed",
        "order_id": request.order_id,
        "issue_description": request.issue_description,
        "preliminary_failure_category": result["failure_category"],
        "policy": result["policy"],
        "order_lookup": result["order_data"],
        "evidence": result["evidence"],
        "recommendation": result["recommendation"],
        "approval_required": result["approval_required"],
        "data_source": result["data_source"],
    }
