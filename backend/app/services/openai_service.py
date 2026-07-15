import json
import os

import requests

from app.models.schemas import QaPackage

SYSTEM_PROMPT = """You are QA Copilot, an expert QA Lead and Engineering Coach.

You are refining a deterministic QA draft, not generating from scratch.
Rules:
- Return valid JSON matching the QaPackage schema only.
- Keep every section grounded in the story, title, domain, acceptance criteria, and baseline draft.
- Do not invent API endpoints, background systems, workflows, roles, or compliance rules unless they are explicitly stated.
- If information is missing, add it to requirement_gaps, assumptions, or open_questions instead of guessing.
- Make test cases specific and traceable to acceptance criteria where possible.
- Return a coverage_score object with realistic 0-100 scoring for acceptance-criteria coverage, negative-path depth, integration depth, and overall coverage.
- Preserve useful baseline content and improve precision, coverage, and prioritization.
"""


def _serialize_package(package: QaPackage) -> str:
    if hasattr(package, 'model_dump_json'):
        return package.model_dump_json(indent=2)
    return package.json(indent=2)


def ask_with_openai(question: str, title: str, story: str, acceptance_criteria: str, domain: str) -> str:
    api_key = os.getenv('OPENAI_API_KEY', '')
    model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
    if not api_key or not model:
        raise ValueError('OpenAI configuration is missing')

    url = f'{base_url}/chat/completions'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    user_prompt = f'''Answer the QA question below using only the provided context.

Title: {title or 'Not provided'}
Domain: {domain or 'General'}
Story:
{story or 'Not provided'}

Acceptance Criteria:
{acceptance_criteria or 'Not provided'}

Question:
{question}

Rules:
1. Keep the answer concise and useful for a QA engineer.
2. If the context is insufficient, say what is missing instead of guessing.
3. Use short paragraphs or bullets only when needed.
'''
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': 'You are QA Copilot, a concise QA assistant answering questions about a Jira story.'},
            {'role': 'user', 'content': user_prompt},
        ],
        'temperature': 0.2,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content'].strip()


def generate_with_openai(title: str, story: str, acceptance_criteria: str, domain: str, baseline_package: QaPackage) -> QaPackage:
    api_key = os.getenv('OPENAI_API_KEY', '')
    model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
    if not api_key or not model:
        raise ValueError('OpenAI configuration is missing')

    url = f'{base_url}/chat/completions'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    user_prompt = f'''Refine the QA package below.

Title: {title}
Domain: {domain}
Story:
{story}

Acceptance Criteria:
{acceptance_criteria or 'Not provided'}

Baseline QA Package JSON:
{_serialize_package(baseline_package)}

Refinement goals:
1. Replace generic statements with scenario-specific QA coverage.
2. Add concrete assumptions and open questions where the story is incomplete.
3. Map acceptance criteria to relevant test cases.
4. Avoid invented API endpoints. If no endpoint is specified, say so explicitly.
5. Keep the output concise, grounded, and directly usable by a QA engineer.
6. Calibrate coverage_score realistically and explain it briefly in coverage_score.notes.
'''
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_prompt},
        ],
        'temperature': 0.2,
        'response_format': {'type': 'json_object'},
    }
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    content = response.json()['choices'][0]['message']['content']
    return QaPackage(**json.loads(content))