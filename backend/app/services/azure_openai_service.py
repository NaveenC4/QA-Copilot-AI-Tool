import os, json, requests
from app.models.schemas import QaPackage

SYSTEM_PROMPT = """You are QA Copilot, an expert QA Lead and Engineering Coach. Generate a complete QA package from a Jira story. Return valid JSON matching the QaPackage schema only. Include a realistic coverage_score object with 0-100 scoring for acceptance-criteria coverage, negative-path depth, integration depth, and overall coverage."""

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
