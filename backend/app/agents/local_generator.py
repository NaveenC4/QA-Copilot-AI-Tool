from app.models.schemas import AcceptanceCriterionCoverage, QaPackage, TestCase, ApiScenario

SECURITY_KEYWORDS = ['login','password','reset','authentication','account','user','email','token']
PAYMENT_KEYWORDS = ['payment','card','transaction','refund','invoice']
API_KEYWORDS = ['api','endpoint','request','response','service','integration']

def _has_any(text: str, words: list[str]) -> bool:
    t = text.lower()
    return any(w in t for w in words)

def generate_local_package(title: str, story: str, acceptance_criteria: str = '', domain: str = 'General') -> QaPackage:
    full_text = f'''{title}\n{story}\n{acceptance_criteria}'''
    is_security = _has_any(full_text, SECURITY_KEYWORDS)
    is_payment = _has_any(full_text, PAYMENT_KEYWORDS)
    is_api = _has_any(full_text, API_KEYWORDS) or is_security or is_payment
    criteria_lines = [line.strip() for line in acceptance_criteria.splitlines() if line.strip()]

    functional = [
        'Validate successful completion of the main user journey using valid input data.',
        'Validate all acceptance criteria are met from an end-user perspective.',
        'Validate correct confirmation, error, and status messages are displayed.',
        'Validate data is saved, updated, or retrieved correctly after the transaction.',
        'Validate user journey across supported browsers and devices.'
    ]
    if is_security:
        functional += [
            'Validate password reset or authentication flow using a registered user account.',
            'Validate reset or authentication token lifecycle, including generation and expiry.',
            'Validate that sensitive information is not exposed in UI, URL, logs, or API response.'
        ]
    if is_payment:
        functional += ['Validate successful payment or transaction processing using valid test data.']

    negative = [
        'Submit mandatory fields as blank and validate field-level errors.',
        'Submit invalid characters, special characters, and oversized input values.',
        'Validate duplicate submission or repeated request handling.',
        'Validate unauthorized access for users without required permission.',
        'Validate session timeout or expired user session behaviour.'
    ]
    if is_security:
        negative += [
            'Validate expired token or invalid token cannot be reused.',
            'Validate SQL injection and script injection inputs are rejected.',
            'Validate account lock or throttling after repeated invalid attempts.',
            'Validate reset link cannot be reused after successful password update.'
        ]

    test_cases = [
        TestCase(id='TC_001', title='Verify successful happy path flow', preconditions=['Valid user/test data exists','Application is accessible'], steps=['Open the application','Navigate to the feature','Enter valid data','Submit the request'], expected_result='Request is processed successfully and confirmation is displayed.', priority='High', type='Functional'),
        TestCase(id='TC_002', title='Verify mandatory field validation', preconditions=['Application is accessible'], steps=['Open the feature','Leave mandatory fields blank','Submit the form'], expected_result='System displays clear validation messages and does not process the request.', priority='High', type='Negative'),
        TestCase(id='TC_003', title='Verify invalid input validation', preconditions=['Application is accessible'], steps=['Open the feature','Enter invalid or special character values','Submit the form'], expected_result='System rejects invalid input and shows appropriate error messages.', priority='Medium', type='Negative'),
        TestCase(id='TC_004', title='Verify audit/data persistence after successful transaction', preconditions=['Valid test data exists'], steps=['Complete the main user flow','Check database/API/audit history','Validate saved values'], expected_result='Data is stored accurately with correct status and timestamp.', priority='High', type='Integration')
    ]
    if is_security:
        test_cases.append(TestCase(id='TC_005', title='Verify expired or reused token is rejected', preconditions=['User has generated a valid token/link'], steps=['Use an expired or already used token','Submit the request'], expected_result='System rejects the request and displays a secure error message.', priority='High', type='Security'))

    api_coverage = [
        ApiScenario(method='POST', endpoint='/api/v1/request', validation='Valid request payload', expected_status='200/201 Success'),
        ApiScenario(method='POST', endpoint='/api/v1/request', validation='Missing mandatory fields', expected_status='400 Bad Request'),
        ApiScenario(method='POST', endpoint='/api/v1/request', validation='Unauthorized request', expected_status='401 Unauthorized'),
        ApiScenario(method='POST', endpoint='/api/v1/request', validation='User without required role', expected_status='403 Forbidden'),
        ApiScenario(method='POST', endpoint='/api/v1/request', validation='Repeated requests beyond threshold', expected_status='429 Too Many Requests')
    ] if is_api else [ApiScenario(method='GET/POST', endpoint='To be confirmed', validation='API endpoint not clearly defined in ticket', expected_status='To be confirmed')]

    gaps = [
        'Exact validation rules are not fully defined.',
        'Role/permission matrix is not specified.',
        'Error message wording is not confirmed.',
        'Audit logging and reporting requirements are not clearly stated.',
        'Supported browsers/devices and non-functional requirements are not mentioned.'
    ]
    if is_security:
        gaps += ['Token expiry duration and reuse policy should be explicitly confirmed.','Password/security policy should be defined clearly.','Rate limiting and account lock rules should be specified.']

    risk_score = 'High' if is_security or is_payment else 'Medium'
    risk_reason = 'The feature impacts authentication/security or financial/user-sensitive flows, so defects may create business, compliance, or user trust issues.' if risk_score == 'High' else 'The feature has moderate business impact and requires validation across functional, negative, and integration paths.'

    playwright = """import { test, expect } from '@playwright/test';

test.describe('AI Generated QA Copilot Test Skeleton', () => {
  test('should complete the happy path successfully', async ({ page }) => {
    await page.goto('https://your-test-url.example.com');
    // TODO: Navigate to feature
    // TODO: Enter valid test data
    // TODO: Submit request
    // TODO: Assert success confirmation
    await expect(page.locator('body')).toBeVisible();
  });

  test('should show validation for mandatory fields', async ({ page }) => {
    await page.goto('https://your-test-url.example.com');
    // TODO: Submit form without mandatory data
    // TODO: Assert field-level validation messages
    await expect(page.locator('body')).toBeVisible();
  });
});"""

    assumptions = [
        'The story describes a single user journey rather than multiple variants.',
        'Test data and environment access can be prepared by the QA team.',
    ]
    if is_security:
        assumptions.append('The reset token is single-use and should not expose account existence.')

    open_questions = [
        'What are the exact validation rules and field formats?',
        'Which user roles or permissions can access this capability?',
        'What browsers, devices, and supported platforms are in scope?',
    ]
    if is_security:
        open_questions += [
            'What is the password policy for the new password?',
            'Should password reset invalidate active sessions on other devices?',
        ]

    acceptance_mapping = []
    for index, criterion in enumerate(criteria_lines, start=1):
        covered_by = ['TC_001', 'TC_004'] if index <= 2 else ['TC_001']
        if is_security and index >= 3:
            covered_by.append('TC_005')
        acceptance_mapping.append(
            AcceptanceCriterionCoverage(
                criterion=criterion,
                covered_by=covered_by,
                notes='Coverage should be refined once exact UI and API flows are confirmed.',
            )
        )

    return QaPackage(
        requirement_summary='The requirement describes a user-facing capability that must be validated for happy path, negative path, boundary conditions, security, data validation, and integration behaviour.',
        functional_scenarios=functional,
        negative_scenarios=negative,
        test_cases=test_cases,
        api_coverage=api_coverage,
        requirement_gaps=gaps,
        automation_recommendation='Recommended for Playwright automation. Prioritize happy path, mandatory validation, invalid input, and key regression scenarios. API coverage can be automated using Postman/Newman or REST-assured depending on team standards.',
        risk_score=risk_score,
        risk_reason=risk_reason,
        playwright_skeleton=playwright,
        business_impact='Estimated reduction of 60-90% in QA preparation effort by generating first-draft test assets in seconds.',
        assumptions=assumptions,
        open_questions=open_questions,
        acceptance_criteria_mapping=acceptance_mapping,
    )
