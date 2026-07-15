import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import TicketRequest, QaPackage
from app.agents.local_generator import generate_local_package
from app.services.openai_service import generate_with_openai
from app.services.azure_openai_service import generate_with_azure_openai

load_dotenv()
app = FastAPI(title='QA Copilot API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])


def get_runtime_config() -> dict:
    use_ai = os.getenv('USE_AI', 'false').lower() == 'true'
    provider = os.getenv('AI_PROVIDER', 'openai').lower() if use_ai else 'local'
    return {'use_ai': use_ai, 'provider': provider}


def generate_with_ai_provider(request: TicketRequest) -> QaPackage:
    provider = os.getenv('AI_PROVIDER', 'openai').lower()
    title = request.title or ''
    story = request.story
    acceptance_criteria = request.acceptance_criteria or ''
    domain = request.domain or 'General'
    baseline_package = generate_local_package(title, story, acceptance_criteria, domain)

    if provider == 'azure':
        return generate_with_azure_openai(title, story, acceptance_criteria, domain)
    if provider == 'openai':
        return generate_with_openai(title, story, acceptance_criteria, domain, baseline_package)
    raise ValueError(f'Unsupported AI_PROVIDER: {provider}')

@app.get('/')
def health():
    return {'status':'QA Copilot API is running', 'docs':'/docs'}


@app.get('/config')
def config():
    return get_runtime_config()

@app.post('/generate', response_model=QaPackage)
def generate_qa_package(request: TicketRequest):
    if os.getenv('USE_AI','false').lower() == 'true':
        try:
            return generate_with_ai_provider(request)
        except Exception as ex:
            print(f'AI provider failed, using local generator. Error: {ex}')
    return generate_local_package(request.title or '', request.story, request.acceptance_criteria or '', request.domain or 'General')
