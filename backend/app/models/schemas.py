from pydantic import BaseModel, Field
from typing import List, Optional

class TicketRequest(BaseModel):
    title: Optional[str] = Field(default='', description='Jira ticket title')
    story: str = Field(..., description='User story, requirement, or Jira ticket description')
    acceptance_criteria: Optional[str] = Field(default='', description='Acceptance criteria')
    domain: Optional[str] = Field(default='General', description='Business domain')

class TestCase(BaseModel):
    id: str
    title: str
    preconditions: List[str]
    steps: List[str]
    expected_result: str
    priority: str
    type: str

class ApiScenario(BaseModel):
    method: str
    endpoint: str
    validation: str
    expected_status: str

class QaPackage(BaseModel):
    requirement_summary: str
    functional_scenarios: List[str]
    negative_scenarios: List[str]
    test_cases: List[TestCase]
    api_coverage: List[ApiScenario]
    requirement_gaps: List[str]
    automation_recommendation: str
    risk_score: str
    risk_reason: str
    playwright_skeleton: str
    business_impact: str
