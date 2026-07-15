from pydantic import BaseModel, Field
from typing import List, Optional

class TicketRequest(BaseModel):
    title: Optional[str] = Field(default='', description='Jira ticket title')
    story: str = Field(..., description='User story, requirement, or Jira ticket description')
    acceptance_criteria: Optional[str] = Field(default='', description='Acceptance criteria')
    domain: Optional[str] = Field(default='General', description='Business domain')


class AskAiRequest(BaseModel):
    question: str = Field(..., min_length=1, description='Question to ask AI')
    asked_count: int = Field(..., ge=1, le=5, description='1-based number of the current question attempt')
    title: Optional[str] = Field(default='', description='Jira ticket title')
    story: Optional[str] = Field(default='', description='User story or requirement')
    acceptance_criteria: Optional[str] = Field(default='', description='Acceptance criteria')
    domain: Optional[str] = Field(default='General', description='Business domain')


class AskAiResponse(BaseModel):
    answer: str
    asked_count: int = Field(..., ge=1, le=5)
    remaining_questions: int = Field(..., ge=0, le=4)

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


class AcceptanceCriterionCoverage(BaseModel):
    criterion: str
    covered_by: List[str] = Field(default_factory=list)
    notes: str = ''


class CoverageScore(BaseModel):
    overall: int = Field(..., ge=0, le=100)
    acceptance_criteria: int = Field(..., ge=0, le=100)
    negative_paths: int = Field(..., ge=0, le=100)
    integration: int = Field(..., ge=0, le=100)
    notes: str = ''

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
    assumptions: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    acceptance_criteria_mapping: List[AcceptanceCriterionCoverage] = Field(default_factory=list)
    coverage_score: CoverageScore
