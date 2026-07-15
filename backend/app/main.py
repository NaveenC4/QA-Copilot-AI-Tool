import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import TicketRequest, QaPackage
from app.agents.local_generator import generate_local_package
from app.services.azure_openai_service import generate_with_azure_openai

load_dotenv()
app = FastAPI(title='QA Copilot API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.get('/')
def health():
    return {'status':'QA Copilot API is running', 'docs':'/docs'}

@app.post('/generate', response_model=QaPackage)
def generate_qa_package(request: TicketRequest):
    if os.getenv('USE_AI','false').lower() == 'true':
        try:
            return generate_with_azure_openai(request.title or '', request.story, request.acceptance_criteria or '', request.domain or 'General')
        except Exception as ex:
            print(f'AI provider failed, using local generator. Error: {ex}')
    return generate_local_package(request.title or '', request.story, request.acceptance_criteria or '', request.domain or 'General')
