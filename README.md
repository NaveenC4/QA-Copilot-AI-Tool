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
Windows easiest command:

```bat
run-backend.bat
```

Run it from the project root. It will:
- create `backend/.venv` if missing
- install `backend/requirements.txt`
- start FastAPI on `http://127.0.0.1:8000`

Manual fallback:

```bash
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Run Frontend
Open `frontend/index.html` in a browser or run:
```bash
cd frontend
python -m http.server 3000
```

## Free Deployment

Recommended deployment for this repo:
- Frontend: Cloudflare Pages
- Backend: Hugging Face Spaces using Docker

This is the path to use for this project.

Detailed checklist:
- `docs/deployment-checklist.md`

### 1. Deploy Backend To Hugging Face Spaces

This repo now includes a root `Dockerfile` for the FastAPI backend.

Steps:
1. Create a new Hugging Face Space
2. Choose `Docker` as the Space SDK
3. Push this repository to the Space
4. Add your runtime secrets in the Space settings if you use AI providers:
	 - `USE_AI`
	 - `AI_PROVIDER`
	 - `OPENAI_API_KEY`
	 - `OPENAI_MODEL`
	 - `OPENAI_BASE_URL`
	 - `AZURE_OPENAI_ENDPOINT`
	 - `AZURE_OPENAI_API_KEY`
	 - `AZURE_OPENAI_DEPLOYMENT`
	 - `AZURE_OPENAI_API_VERSION`

Your backend URL will look like:

```text
https://your-space-name.hf.space
```

### 2. Deploy Frontend To Cloudflare Pages

Deploy the `frontend` folder as a static site.

Before deploying, update `frontend/config.js`:

```js
window.QA_COPILOT_CONFIG = {
	BACKEND_URL: 'https://your-space-name.hf.space',
};
```

Then deploy the `frontend` directory to Cloudflare Pages.

### 3. Local Development Note

For local development, keep `frontend/config.js` as:

```js
window.QA_COPILOT_CONFIG = {
	BACKEND_URL: 'http://127.0.0.1:8000',
};
```

## Optional Azure OpenAI Setup
Copy `backend/.env.example` to `backend/.env` and update values.

## Hackathon Pitch
QA Copilot is an Agentic AI assistant that transforms Jira stories into a complete QA package including test scenarios, negative testing, API coverage, risk assessment, requirement gaps, and automation recommendations in seconds, reducing QA preparation effort by up to 80-90% while improving sprint readiness and test coverage.
