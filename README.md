# QA Copilot - AI Powered Sprint Readiness Assistant

QA Copilot is a hackathon-ready AI tool that turns a Jira/User Story into a first-draft QA package.

It generates:
- Requirement summary
- Functional test scenarios
- Negative test scenarios
- API test coverage
- Requirement gaps
- Risk assessment
- Automation recommendation
- Starter Playwright test skeleton

## Problem Solved
QA teams spend hours reading Jira stories, understanding acceptance criteria, identifying missing requirements, and preparing test assets. QA Copilot reduces this effort by generating the first draft within seconds.

## Target Users
- QA Engineers
- Automation Engineers
- QA Leads
- Scrum Teams

## Architecture
```text
User Story / Jira Ticket -> Requirement Analyzer -> Gap Detector -> Test Designer -> API Coverage Agent -> Automation Coach -> Risk Reviewer -> Final QA Package
```

## Tech Stack
- Backend: Python FastAPI
- Frontend: HTML, CSS, JavaScript
- Optional AI Provider: Azure OpenAI / OpenAI-compatible endpoint
- Fallback Mode: Rule-based local generator for demo without API key

## Run Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run Frontend
Open `frontend/index.html` in a browser or run:
```bash
cd frontend
python -m http.server 3000
```

## Optional Azure OpenAI Setup
Copy `backend/.env.example` to `backend/.env` and update values.

## Hackathon Pitch
QA Copilot is an Agentic AI assistant that transforms Jira stories into a complete QA package including test scenarios, negative testing, API coverage, risk assessment, requirement gaps, and automation recommendations in seconds, reducing QA preparation effort by up to 80-90% while improving sprint readiness and test coverage.
