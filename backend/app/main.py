import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import AskAiRequest, AskAiResponse, TicketRequest, QaPackage
from app.agents.local_generator import generate_local_package
from app.services.attachment_parser import extract_attachment_text, parse_attachment_content
from app.services.openai_service import ask_with_openai, generate_with_openai
from app.services.azure_openai_service import ask_with_azure_openai, generate_with_azure_openai

load_dotenv()
app = FastAPI(title='QA Copilot API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])


def get_runtime_config() -> dict:
    use_ai = os.getenv('USE_AI', 'false').lower() == 'true'
    provider = os.getenv('AI_PROVIDER', 'openai').lower() if use_ai else 'local'
    model = ''
    if use_ai:
        if provider == 'openai':
            model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        elif provider == 'azure':
            model = os.getenv('AZURE_OPENAI_DEPLOYMENT', '')
    return {'use_ai': use_ai, 'provider': provider, 'model': model}


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


def build_qa_package(request: TicketRequest) -> QaPackage:
    if os.getenv('USE_AI','false').lower() == 'true':
        try:
            return generate_with_ai_provider(request)
        except Exception as ex:
            print(f'AI provider failed, using local generator. Error: {ex}')
    return generate_local_package(request.title or '', request.story, request.acceptance_criteria or '', request.domain or 'General')


def answer_question_locally(request: AskAiRequest) -> str:
    context_bits = []
    if request.title:
        context_bits.append(f'Title: {request.title}')
    if request.domain:
        context_bits.append(f'Domain: {request.domain}')
    if request.story:
        context_bits.append(f'Story: {request.story}')
    if request.acceptance_criteria:
        context_bits.append(f'Acceptance Criteria: {request.acceptance_criteria}')
    context_text = '\n'.join(context_bits).strip()
    if not context_text:
        return 'No story context is available. Add a title, story, or acceptance criteria before asking AI.'
    return f"This environment is using the local fallback instead of cloud AI. Based on the current story context, the key QA guidance is to validate the requested behavior against the stated acceptance criteria, cover negative paths, and flag any missing details before test design.\n\nQuestion: {request.question}\n\nAvailable context:\n{context_text[:1400]}"


def answer_with_provider(request: AskAiRequest) -> str:
    if os.getenv('USE_AI', 'false').lower() != 'true':
        return answer_question_locally(request)

    provider = os.getenv('AI_PROVIDER', 'openai').lower()
    title = request.title or ''
    story = request.story or ''
    acceptance_criteria = request.acceptance_criteria or ''
    domain = request.domain or 'General'

    if provider == 'azure':
        return ask_with_azure_openai(request.question, title, story, acceptance_criteria, domain)
    if provider == 'openai':
        return ask_with_openai(request.question, title, story, acceptance_criteria, domain)
    raise ValueError(f'Unsupported AI_PROVIDER: {provider}')

@app.get('/')
def health():
    return {'status':'QA Copilot API is running', 'docs':'/docs'}


@app.get('/config')
def config():
    return get_runtime_config()

@app.post('/generate', response_model=QaPackage)
def generate_qa_package(request: TicketRequest):
    return build_qa_package(request)


@app.post('/ask-ai', response_model=AskAiResponse)
def ask_ai(request: AskAiRequest):
    if request.asked_count > 5:
        raise HTTPException(status_code=400, detail='Ask AI limit reached. Maximum 5 questions allowed.')

    try:
        answer = answer_with_provider(request)
    except Exception as error:
        if os.getenv('USE_AI', 'false').lower() == 'true':
            print(f'AI question answer failed, using local fallback. Error: {error}')
        answer = answer_question_locally(request)

    return AskAiResponse(
        answer=answer,
        asked_count=request.asked_count,
        remaining_questions=max(0, 5 - request.asked_count),
    )


@app.post('/generate-with-attachment', response_model=QaPackage)
def generate_with_attachment(
    title: str = Form(default=''),
    domain: str = Form(default='General'),
    story: str = Form(default=''),
    acceptance_criteria: str = Form(default=''),
    attachment: UploadFile = File(...),
):
    try:
        attachment_text = extract_attachment_text(attachment)
        parsed_title, parsed_domain, parsed_story, parsed_criteria = parse_attachment_content(attachment_text, attachment.filename or '')
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    merged_request = TicketRequest(
        title=title.strip() or parsed_title,
        domain=domain.strip() or parsed_domain or 'General',
        story=story.strip() or parsed_story or attachment_text,
        acceptance_criteria=acceptance_criteria.strip() or parsed_criteria,
    )
    return build_qa_package(merged_request)


@app.post('/preview-attachment')
def preview_attachment(attachment: UploadFile = File(...)):
    try:
        attachment_text = extract_attachment_text(attachment)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    preview_text = attachment_text.strip() or 'No readable text was found in this attachment.'
    return {
        'filename': attachment.filename or 'attachment',
        'preview': preview_text[:12000],
        'truncated': len(preview_text) > 12000,
    }
