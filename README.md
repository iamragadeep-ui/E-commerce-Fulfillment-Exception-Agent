# E-commerce-Fulfillment-Exception-Agent
# E-commerce Fulfillment Exception Agent

An agentic AI project that investigates e-commerce fulfillment issues, identifies likely failure categories, gathers supporting evidence, retrieves relevant policies, and recommends next steps.

## Project Goals

- Investigate delayed orders and fulfillment exceptions.
- Classify issues such as carrier delays, inventory shortages, address issues, and warehouse delays.
- Retrieve relevant policy guidance.
- Provide evidence and recommendations for human review.
- Apply input validation and approval safeguards.

## Architecture

- **FastAPI:** Exposes the REST API.
- **LangGraph:** Orchestrates the investigation workflow.
- **Pydantic:** Validates incoming request data.
- **Guardrails:** Rejects empty or invalid inputs.
- **Policy retrieval:** Retrieves predefined demo policy guidance.
- **Simulated order lookups:** Provides sample order and fulfillment information.

## Workflow

1. Receive an order ID and issue description.
2. Validate the request.
3. Classify the reported issue.
4. Look up the order in simulated data.
5. Retrieve the matching policy.
6. Generate a recommendation.
7. Flag the recommendation for approval.

## Technology Stack

Python, FastAPI, Uvicorn, LangGraph, Pydantic, and Pytest.

## Prerequisites

- Python 3.11
- Git
- Visual Studio Code (recommended)

## Local Setup

Clone the repository:

```bash
git clone https://github.com/iamragadeep-ui/E-commerce-Fulfillment-Exception-Agent.git
cd E-commerce-Fulfillment-Exception-Agent
```

Create and activate a virtual environment on Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the API:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Open the interactive API documentation at http://127.0.0.1:8000/docs.

## Run Tests

```powershell
python -m pytest
```

## API Example

Endpoint: `POST /exceptions`

Example request:

```json
{
  "order_id": "ORD-1004",
  "issue_description": "The order has a warehouse processing delay"
}
```

The API returns the preliminary failure category, simulated order lookup, evidence, policy guidance, recommendation, and approval requirement.

## Important Limitations

This project uses simulated order records and predefined demo policies. It is not connected to a real retailer, inventory system, warehouse, payment platform, or carrier. Recommendations should be reviewed by a human; the demo does not execute real fulfillment actions.

## Future Enhancements

- Integrate authorized real-world order and carrier APIs.
- Add document-based policy retrieval.
- Improve classification using retrieval-augmented generation.
- Add authentication, logging, and deployment configuration.
- Add a human approval interface.
