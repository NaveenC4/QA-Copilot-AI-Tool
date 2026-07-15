# Deployment Checklist

Use this deployment path for the project:
- Frontend: Cloudflare Pages
- Backend: Hugging Face Spaces using Docker

## Backend: Hugging Face Spaces

### Create the Space
1. Open Hugging Face and create a new Space.
2. Set the Space SDK to `Docker`.
3. Connect the GitHub repository or push the repository to the Space.
4. Keep the repository root unchanged so Hugging Face can use the root `Dockerfile`.

### Configure environment variables
Add these variables in the Space settings as needed:

Required for local fallback only:
- `USE_AI=false`

Required for OpenAI:
- `USE_AI=true`
- `AI_PROVIDER=openai`
- `OPENAI_API_KEY=...`
- `OPENAI_MODEL=gpt-4o-mini`

Optional for OpenAI-compatible endpoints:
- `OPENAI_BASE_URL=...`

Required for Azure OpenAI:
- `USE_AI=true`
- `AI_PROVIDER=azure`
- `AZURE_OPENAI_ENDPOINT=...`
- `AZURE_OPENAI_API_KEY=...`
- `AZURE_OPENAI_DEPLOYMENT=...`
- `AZURE_OPENAI_API_VERSION=2024-02-15-preview`

### Validate the backend
After deployment completes:
1. Open the Space URL.
2. Confirm the root endpoint returns the API status.
3. Open `/docs` and verify the FastAPI Swagger UI loads.
4. Test `GET /config` and confirm the provider settings look correct.

Expected URL shape:

```text
https://your-space-name.hf.space
```

## Frontend: Cloudflare Pages

### Update frontend config
Edit `frontend/config.js` and set:

```js
window.QA_COPILOT_CONFIG = {
  BACKEND_URL: 'https://your-space-name.hf.space',
};
```

### Create the Pages project
1. Open Cloudflare Pages.
2. Create a new project from this repository.
3. Set the root directory to `frontend`.
4. Leave the build command empty.
5. Set the output directory to `.`.
6. Deploy.

### Validate the frontend
After deployment completes:
1. Open the Pages URL.
2. Sign in with the demo credentials.
3. Confirm the dashboard loads.
4. Generate a QA package.
5. Open `Ask AI` and confirm the modal works.
6. Upload a supported file and confirm preview plus remove both work.

## Demo credentials

Use the current frontend demo login:
- Email: `demo@qacopilot.ai`
- Password: `qa123`

## Smoke test after both deployments

Run this order:
1. Open the frontend login page.
2. Sign in.
3. Generate a story without attachment.
4. Generate a story with attachment.
5. Ask one AI question.
6. Refresh the page and confirm the app still loads correctly.

## Common fixes

- If the frontend loads but API calls fail, recheck `frontend/config.js`.
- If the backend Space fails to build, confirm the Space is using `Docker` and the root `Dockerfile` is present.
- If AI responses fall back to local mode, verify `USE_AI` and the provider-specific secrets.