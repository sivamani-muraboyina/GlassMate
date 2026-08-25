# GlassMate — GitHub Copilot Instructions

## 1. PROJECT CONTEXT

GlassMate is a portfolio-grade GenAI application that helps students
and job seekers discover relevant jobs, evaluate their fit, select
appropriate resumes, prepare applications, validate generated content,
and track applications and follow-ups.

GlassMate is NOT a generic chatbot, generic RAG application, or simple
resume generator.

The system uses specialized AI agents, deterministic backend services,
PostgreSQL, controlled tools/MCP, external integrations, and a critic
agent.

The user is the source of truth for their personal/career information.

The database is the source of truth for stored application data.

LLMs may interpret, classify, summarize, recommend, and generate
proposals.

LLMs must NOT silently modify authoritative candidate information.

--------------------------------------------------
## 2. DEVELOPMENT PRINCIPLE
--------------------------------------------------

Build GlassMate incrementally.

NEVER attempt to implement the entire project at once.

The project is divided into explicit phases in PROJECT_SPEC.md.

Only implement the phase explicitly requested by the user.

Do NOT automatically implement future phases.

Before implementing a phase:

1. Read PROJECT_SPEC.md.
2. Read DEVELOPMENT.md.
3. Inspect the existing repository.
4. Understand the current architecture.
5. Reuse existing components where appropriate.
6. Avoid unnecessary rewrites.

After implementing a phase:

1. Run tests.
2. Fix errors caused by your implementation.
3. Report files changed.
4. Report dependencies added.
5. Report tests executed and results.
6. Report assumptions.
7. Report incomplete work.
8. Update DEVELOPMENT.md only for the current phase.
9. Do NOT mark future phases complete.

--------------------------------------------------
## 3. ARCHITECTURE RULE
--------------------------------------------------

Do not change the project's fundamental architecture without asking.

The intended architecture is:

User
 ↓
Orchestrator
 ↓
Specialized Agents
 ↓
Controlled Tools / MCP
 ↓
Services / Repositories
 ↓
PostgreSQL

External integrations may include:

GitHub
Gmail
Google Calendar
Permitted job sources
LLM providers

The orchestrator coordinates workflows.

The orchestrator should NOT become a giant autonomous LLM with
dozens of tools.

Use deterministic Python workflow logic whenever possible.

Use an LLM only when reasoning, semantic interpretation, generation,
classification, or synthesis is actually needed.

--------------------------------------------------
## 4. AGENT BOUNDARIES
--------------------------------------------------

GlassMate uses specialized agents.

Core agents:

1. Job Discovery Agent
2. Candidate Intelligence Agent
3. Company Intelligence Agent
4. Job Match Agent
5. Resume Strategy Agent
6. Resume Proposal Agent
7. Application Agent
8. Critic Agent
9. Gmail Agent
10. Calendar component/agent

Each agent should have a narrow responsibility.

Do NOT create a single "Super Agent" with all available tools.

Do NOT give agents tools they do not need.

Agents should operate with the minimum context and minimum tool
permissions required for their task.

--------------------------------------------------
## 5. AGENT VS DETERMINISTIC CODE
--------------------------------------------------

Do NOT create an agent for every feature.

Use normal deterministic code for:

- database operations
- CRUD
- authentication
- authorization
- scoring formulas
- thresholds
- versioning
- duplicate detection
- state transitions
- validation
- file handling
- LaTeX compilation
- calendar event creation
- application timestamps
- retry limits
- workflow control

Use LLM agents for tasks such as:

- semantic JD analysis
- semantic candidate/JD comparison
- project summarization
- company synthesis
- resume strategy
- resume generation
- application content generation
- critique

The goal is not maximum agent count.

The goal is appropriate separation of responsibilities.

--------------------------------------------------
## 6. DATABASE RULES
--------------------------------------------------

PostgreSQL is the source of truth.

Agents must NOT receive unrestricted SQL access.

Do NOT give an LLM a tool such as:

execute_arbitrary_sql()

Do NOT allow an agent to freely modify database records.

Prefer typed service/repository functions such as:

get_candidate_profile()
get_candidate_skills()
get_projects()
get_project()
get_resume()
get_resume_versions()
get_job()
get_application_history()
get_user_preferences()

Use explicit proposal/action functions where required.

Example:

create_resume_proposal()

Do NOT allow the LLM to directly overwrite approved resume data.

--------------------------------------------------
## 7. CANDIDATE DATA IS AUTHORITATIVE
--------------------------------------------------

Candidate information is treated as factual source data.

Examples:

- skills
- education
- experience
- employers
- dates
- projects
- achievements
- GitHub repositories
- approved resume information

The system must NEVER invent:

- skills
- employers
- projects
- education
- experience
- dates
- achievements
- metrics
- certifications

If information is unavailable:

return UNKNOWN/null where appropriate.

Do not guess.

--------------------------------------------------
## 8. EVIDENCE-GROUNDED GENERATION
--------------------------------------------------

Important candidate claims should be traceable to evidence.

Candidate evidence may come from:

- approved resume
- GitHub project
- candidate profile
- education
- experience
- other explicitly provided sources

Where practical, store evidence references.

Example:

Claim:
"Built an LLM evaluation pipeline."

Evidence:
project_id = 17

The Critic Agent should be able to verify important claims against
stored evidence.

--------------------------------------------------
## 9. RESUME RULES
--------------------------------------------------

The user provides at least three approved resumes.

Approved resumes are immutable.

Never overwrite an approved resume.

When creating a new resume:

create a new ResumeVersion.

Statuses may include:

PROPOSED
APPROVED
REJECTED

A generated resume begins as:

PROPOSED

Only explicit user approval can make it:

APPROVED

Resume generation may:

- reorder relevant content
- select relevant projects
- emphasize existing skills
- rewrite existing bullets
- modify the summary
- remove irrelevant content
- create a proposed resume using the user's Overleaf/LaTeX template

Resume generation may NOT:

- invent skills
- invent experience
- invent projects
- invent metrics
- invent employers
- invent dates
- invent education
- invent achievements

--------------------------------------------------
## 10. JOB MATCHING
--------------------------------------------------

The Job Match Agent evaluates the relationship between a job and
the candidate.

Requirements should be classified as:

SUPPORTED
PARTIALLY_SUPPORTED
NOT_SUPPORTED
UNKNOWN

The LLM may perform semantic classification.

The final numerical match score should be calculated by deterministic
code rather than allowing the LLM to arbitrarily choose the final score.

Initial categories:

>70% = STRONG MATCH

50-70% = NEAR MATCH

<50% = POOR MATCH

These thresholds should be configurable.

For a NEAR MATCH:

do not automatically invent a new career direction.

Explain:

- candidate strengths
- missing requirements
- relevant existing evidence
- possible resume direction

--------------------------------------------------
## 11. UNKNOWN HANDLING
--------------------------------------------------

Unknown information must remain unknown.

Examples:

If salary is not explicitly available:

salary = UNKNOWN/null

If applicant count is unavailable:

applicant_count = UNKNOWN/null

Do NOT estimate.

Do NOT generate plausible numbers.

Do NOT convert guesses into facts.

When external information conflicts:

preserve the uncertainty and identify the source.

--------------------------------------------------
## 12. COMPANY INFORMATION
--------------------------------------------------

Company Intelligence must distinguish:

VERIFIED
INFERRED
UNKNOWN

Do not fabricate:

- salary
- company size
- funding
- founders
- revenue
- location
- hiring details

unless supported by available evidence.

The user specifically wants concise company information, especially:

- company name
- role
- short company summary
- salary if explicitly available
- location
- relevant company information

--------------------------------------------------
## 13. GITHUB PROJECT UNDERSTANDING
--------------------------------------------------

GitHub project understanding is primarily a one-time/cached process.

For a repository:

- read README
- inspect basic metadata
- identify technologies
- summarize purpose
- create a basic architecture description
- store evidence

Do NOT repeatedly process the same repository for every job.

Cache project understanding.

Allow explicit refresh when needed.

Do not claim the candidate personally built something unless evidence
supports that claim.

--------------------------------------------------
## 14. LLM USAGE
--------------------------------------------------

The system is designed to be free-tier-first.

Use a provider abstraction.

Potential providers may include:

- OpenAI
- Anthropic
- Groq
- Google/Gemini
- other legitimately available providers

The system should support multiple providers through a common interface.

Do NOT hard-code the entire application to one provider.

Do NOT expose API keys in source code.

Do NOT commit API keys.

Use environment variables or secure secret management.

Do NOT design account/key rotation specifically to bypass provider
rate limits or terms.

Use smaller/cheaper/free models for simple tasks when appropriate.

Use stronger models only when reasoning quality actually requires them.

--------------------------------------------------
## 15. STRUCTURED LLM OUTPUT
--------------------------------------------------

Prefer structured outputs using Pydantic models.

Avoid relying on free-form text when the application needs structured
data.

For example:

JobAnalysis
RequirementMatch
CompanySummary
ResumeProposal
CriticResult

Validate LLM outputs before storing or using them.

Invalid outputs should be rejected/retried safely.

--------------------------------------------------
## 16. CRITIC AGENT
--------------------------------------------------

The Critic Agent is an independent validation component.

Its purpose is to TRY TO FIND ERRORS.

It should check:

- unsupported candidate claims
- invented skills
- invented experience
- altered dates
- altered numbers
- incorrect company information
- JD mismatch
- missing requirements
- duplicate application
- incomplete application materials
- inconsistency between resume and application

Output:

PASS
or
FAIL

with:

- issue
- severity
- evidence
- correction recommendation

Do not allow unlimited agent loops.

Maximum revision attempts should be limited.

The critic should not simply repeat the generator's reasoning.

--------------------------------------------------
## 17. HUMAN APPROVAL
--------------------------------------------------

Human approval is required before important external actions when
the workflow specifies it.

Examples:

- approving a new resume
- sending a cold email
- final application submission where platform automation is not
  supported

The system should clearly show:

- what will happen
- which resume will be used
- what content was generated
- important warnings
- critic result

Never hide generated changes from the user.

--------------------------------------------------
## 18. MCP RULES
--------------------------------------------------

MCP should be used as a controlled tool interface where appropriate.

Do NOT use MCP simply because it is available.

Potential MCP/tool integrations:

- GitHub
- Gmail
- Google Calendar
- controlled candidate tools
- controlled resume tools
- controlled application tools

Agents should receive only the tools they require.

Example:

Job Match Agent:

get_job()
get_candidate_skills()
get_projects()

Resume Agent:

get_resume()
get_template()
get_projects()
create_resume_proposal()

Gmail Agent:

search_email()
read_thread()
create_draft()
send_email()

Never expose unrestricted database access through MCP.

--------------------------------------------------
## 19. GMAIL RULES
--------------------------------------------------

Gmail is optional.

Use minimum required OAuth permissions.

Capabilities may include:

- searching relevant emails
- reading relevant threads
- identifying application responses
- identifying interview invitations
- creating drafts
- sending approved emails

Cold outreach must:

generate draft
→ critic
→ human approval
→ send

Do not mass email.

Do not harvest personal contact information.

--------------------------------------------------
## 20. CALENDAR RULES
--------------------------------------------------

Calendar integration is optional.

Before creating a follow-up:

check whether an equivalent reminder already exists.

Do not create unnecessary duplicate reminders.

Use deterministic code for dates and scheduling.

--------------------------------------------------
## 21. LINKEDIN RULES
--------------------------------------------------

Do not implement prohibited LinkedIn automation.

Do NOT create:

- browser automation that imitates user activity
- CAPTCHA bypass
- credential scraping
- rate-limit bypass
- unauthorized scraping
- automated clicking intended to bypass platform restrictions

Keep job-source logic abstract.

For sources where programmatic application is permitted,
application execution may be automated.

For unsupported/prohibited flows, use a platform-compliant handoff.

--------------------------------------------------
## 22. SECURITY
--------------------------------------------------

Follow least privilege.

Protect:

- API keys
- OAuth tokens
- candidate information
- resumes
- email data

Never log secrets.

Never commit .env files.

Use .env.example for configuration documentation.

Do not expose private candidate information in logs unnecessarily.

--------------------------------------------------
## 23. ERROR HANDLING
--------------------------------------------------

External services can fail.

Handle:

- API errors
- rate limits
- invalid LLM responses
- timeouts
- authentication failures
- unavailable job data
- malformed resumes
- LaTeX compilation errors

Use retries only where appropriate.

Retries must have limits.

Do not create infinite retry loops.

Return useful structured errors.

--------------------------------------------------
## 24. TESTING
--------------------------------------------------

Every meaningful feature must have tests.

Prefer:

- unit tests
- integration tests
- mocked external APIs
- agent evaluation tests
- adversarial tests

Do not rely only on manually testing the UI.

Important tests include:

- hallucinated candidate claim detection
- resume immutability
- duplicate applications
- unknown salary handling
- unknown applicant count handling
- requirement matching
- critic detection
- authorization
- tool permissions
- workflow transitions

--------------------------------------------------
## 25. EVALUATION
--------------------------------------------------

The project must have measurable evaluation.

Important metrics:

Job matching:
- Precision
- Recall
- F1

Requirement classification:
- Accuracy
- F1

Resume generation:
- unsupported claim rate
- requirement coverage
- factual consistency
- LaTeX compilation success

Critic:
- false negative rate
- false positive rate

System:
- latency
- LLM calls
- token usage
- failure rate
- human intervention time

Do not claim that a component works merely because a demonstration
looked correct.

Build small labelled evaluation datasets.

--------------------------------------------------
## 26. DEPENDENCY RULES
--------------------------------------------------

Do not add a dependency just because it is popular.

Before adding a dependency:

1. determine whether the standard library or an existing dependency
   is sufficient
2. explain why the dependency is necessary
3. check that it fits the architecture
4. add it only if justified

Avoid unnecessary frameworks.

--------------------------------------------------
## 27. CODE QUALITY
--------------------------------------------------

Prefer:

- type hints
- Pydantic models
- clear interfaces
- small functions
- dependency injection
- service/repository separation
- readable names
- explicit error handling
- testable components

Avoid:

- giant files
- giant classes
- global mutable state
- hidden side effects
- duplicated business logic
- magic constants
- arbitrary LLM decisions where deterministic code is possible

--------------------------------------------------
## 28. PHASE DISCIPLINE
--------------------------------------------------

PROJECT_SPEC.md defines the implementation phases.

Only work on the phase explicitly requested.

If implementing Phase 7:

DO NOT implement Phase 8.

If you discover something needed for a later phase:

document it.

Do not silently implement it.

Do not restructure working previous phases unless necessary.

If a requested feature conflicts with the architecture:

STOP and explain the conflict before making architectural changes.

--------------------------------------------------
## 29. COPILOT BEHAVIOR
--------------------------------------------------

Before making significant changes:

inspect the existing code.

Do not assume files exist.

Do not create duplicate implementations of existing functionality.

After changes:

run relevant tests.

If tests fail because of your changes:

fix them before declaring the phase complete.

At the end of every phase report:

1. Files created
2. Files modified
3. Dependencies added
4. Database migrations
5. Tests added
6. Tests passed
7. Known limitations
8. Assumptions
9. Remaining work

Do NOT proceed to the next phase automatically.

--------------------------------------------------
## 30. MOST IMPORTANT RULE
--------------------------------------------------

Do not optimize for "maximum AI."

Optimize for:

correctness
explainability
security
testability
controlled autonomy
clear agent boundaries
evidence-grounded generation
and measurable evaluation.

GlassMate should demonstrate that the developer understands
when to use an LLM, when NOT to use an LLM, when to use an agent,
when to use deterministic code, and how to control autonomous systems.