import os, json, requests
from app.models.schemas import QaPackage

SYSTEM_PROMPT = """You are QA Copilot, an expert QA Lead and Engineering Coach. Generate a complete QA package from a Jira story. Return valid JSON matching the QaPackage schema only. Include a realistic coverage_score object with 0-100 scoring for acceptance-criteria coverage, negative-path depth, integration depth, and overall coverage."""


def ask_with_azure_openai(question: str, title: str, story: str, acceptance_criteria: str, domain: str) -> str:
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT','').rstrip('/')
    api_key = os.getenv('AZURE_OPENAI_API_KEY','')
    deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT','')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION','2024-02-15-preview')
    if not endpoint or not api_key or not deployment:
        raise ValueError('Azure OpenAI configuration is missing')
    url = f'{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}'
    headers = {'api-key': api_key, 'Content-Type': 'application/json'}
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
    payload = {'messages':[{'role':'system','content':'You are QA Copilot, a concise QA assistant answering questions about a Jira story.'},{'role':'user','content':user_prompt}], 'temperature':0.2}
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content'].strip()

def generate_with_azure_openai(title: str, story: str, acceptance_criteria: str, domain: str) -> QaPackage:
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT','').rstrip('/')
    api_key = os.getenv('AZURE_OPENAI_API_KEY','')
    deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT','')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION','2024-02-15-preview')
    if not endpoint or not api_key or not deployment:
        raise ValueError('Azure OpenAI configuration is missing')
    url = f'{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}'
    headers = {'api-key': api_key, 'Content-Type': 'application/json'}
    user_prompt = f'''Title: {title}\nDomain: {domain}\nStory:\n{story}\n\nAcceptance Criteria:\n{acceptance_criteria}'''
    payload = {'messages':[{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':user_prompt}], 'temperature':0.2, 'response_format':{'type':'json_object'}}
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    content = response.json()['choices'][0]['message']['content']
    return QaPackage(**json.loads(content))
