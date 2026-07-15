from io import BytesIO
from pathlib import Path
import json
import re

from docx import Document
from fastapi import UploadFile
from pypdf import PdfReader


SUPPORTED_ATTACHMENT_TYPES = {'.txt', '.md', '.csv', '.json', '.pdf', '.docx'}


def extract_attachment_text(attachment: UploadFile) -> str:
    suffix = Path(attachment.filename or '').suffix.lower()
    if suffix not in SUPPORTED_ATTACHMENT_TYPES:
        raise ValueError(f'Unsupported attachment type: {suffix or "unknown"}')

    raw_bytes = attachment.file.read()
    if not raw_bytes:
        raise ValueError('Attachment is empty')

    if suffix in {'.txt', '.md', '.csv'}:
        return raw_bytes.decode('utf-8', errors='ignore').strip()

    if suffix == '.json':
        parsed = json.loads(raw_bytes.decode('utf-8', errors='ignore'))
        return json.dumps(parsed, indent=2).strip()

    if suffix == '.pdf':
        reader = PdfReader(BytesIO(raw_bytes))
        text = '\n'.join((page.extract_text() or '').strip() for page in reader.pages)
        return text.strip()

    if suffix == '.docx':
        document = Document(BytesIO(raw_bytes))
        text = '\n'.join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
        return text.strip()

    raise ValueError(f'Unsupported attachment type: {suffix}')


def parse_attachment_content(raw_text: str, fallback_title: str = '') -> tuple[str, str, str, str]:
    text = raw_text.strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = ''
    domain = ''
    story_lines = []
    story = text
    acceptance_criteria = ''

    for line in lines:
        lower = line.lower()
        if lower.startswith('title:'):
            title = line.split(':', 1)[1].strip()
        elif lower.startswith('domain:'):
            domain = line.split(':', 1)[1].strip()
        elif lower.startswith('story:'):
            story_lines.append(line.split(':', 1)[1].strip())
        elif not lower.startswith('acceptance criteria') and not lower.startswith('criteria:'):
            story_lines.append(line)

    criteria_match = re.search(r'(acceptance criteria|criteria)\s*:?\s*', text, flags=re.IGNORECASE)
    if criteria_match:
        story = text[:criteria_match.start()].strip()
        acceptance_criteria = text[criteria_match.end():].strip()

    filtered_story_lines = []
    for line in story.splitlines() if criteria_match else story_lines:
        stripped = line.strip()
        lower = stripped.lower()
        if not stripped:
            continue
        if lower.startswith('title:') or lower.startswith('domain:'):
            continue
        if lower.startswith('story:'):
            stripped = stripped.split(':', 1)[1].strip()
        filtered_story_lines.append(stripped)

    if filtered_story_lines:
        story = '\n'.join(filtered_story_lines).strip()

    if not title:
        title = fallback_title or (lines[0] if lines and len(lines[0]) <= 90 else '')
    if title and story.startswith(title):
        story = story[len(title):].strip(':-\n ')

    if not story:
        story = text

    return title, domain, story, acceptance_criteria