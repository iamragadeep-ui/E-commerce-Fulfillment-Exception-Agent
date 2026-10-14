# E-commerce Fulfillment Exception Agent

This repository is the Phase 1 foundation for a production-oriented, portfolio-ready agentic AI project for e-commerce fulfillment exception investigation.

## Simple architecture explanation

The project has three main parts:

- A FastAPI backend that receives fulfillment requests, validates them, and exposes investigation APIs.
- A LangGraph-based multi-agent workflow that classifies the problem, gathers evidence, retrieves policies, reasons about the root cause, and plans safe recovery actions.
- A frontend operations dashboard that lets human operators review evidence, recommendations, approvals, and execution outcomes.

In plain terms: a user submits an order or exception; the system checks whether the request is allowed; it looks up operational data; it decides what kind of exception it is; it retrieves policies; it reasons about the most likely root cause; it suggests the safest recovery option; then a human must approve any sensitive action before it is executed.

## Phase 1 status

This repository currently contains the project scaffold, environment configuration, and a working FastAPI backend with a health-check endpoint.

## Required software and versions

- Python 3.12.x (recommended for compatibility with the pinned dependency stack)
- FastAPI 0.111.1
- Uvicorn 0.30.1
- Pydantic 2.8.2
- SQLAlchemy 2.0.31
- PostgreSQL for production, SQLite for local development
- Node.js 18+ and Next.js for the frontend in later phases
- Docker and Docker Compose for local orchestration
- pytest 8.3.2

## VS Code project folder creation

Create the repository in the workspace root and keep the following structure:

- backend/
- backend/app/
- backend/app/api/
- backend/app/agents/
- backend/app/graph/
- backend/app/tools/
- backend/app/guardrails/
- backend/app/rag/
- backend/app/models/
- backend/app/schemas/
- backend/app/services/
- backend/app/database/
- backend/app/security/
- backend/app/evaluation/
- backend/app/observability/
- frontend/
- data/
- scripts/
- tests/
- docs/

## Windows PowerShell commands

```powershell
cd C:\path\to\workspace
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Python virtual environment setup

```bash
cd /workspaces/E-commerce-Fulfillment-Exception-Agent
python3.12 -m venv .venv
. .venv/bin/activate
python --version
```

## Backend dependency installation

```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

## Initial FastAPI application

The project includes a minimal app entry point in [backend/app/main.py](backend/app/main.py) and environment settings in [backend/app/config.py](backend/app/config.py).

## Health-check endpoint

The app exposes:

- GET /health
- GET /

The code returns a JSON payload with the service status and environment metadata.

## Commands to start the backend

```bash
cd /workspaces/E-commerce-Fulfillment-Exception-Agent/backend
. ../.venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Expected output

The server should report a successful startup with output similar to:

```text
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Verification steps

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok","service":"E-commerce Fulfillment Exception Agent","version":"0.1.0","environment":"development","debug":true}
```

The Phase 1 backend check is complete and verified. We are now waiting for confirmation before proceeding to Phase 2.
