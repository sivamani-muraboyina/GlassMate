I am building a portfolio-grade GenAI project called:

GlassMate

It is an AI-powered job discovery, evaluation, application preparation,
and application tracking system.

The goal is NOT to build a generic chatbot, RAG application, or resume
generator.

The system should solve a real problem:

A student/job seeker provides their candidate information, approved
resumes, GitHub projects, job preferences, and optionally Gmail/Calendar.
The system finds relevant jobs, evaluates the candidate-job fit, researches
the company using available job/company information, selects the most
appropriate existing resume, suggests when a new resume direction may be
useful, prepares application materials, validates them against candidate
evidence, and tracks applications and follow-ups.

The system should minimize unnecessary human effort while preventing
fabricated candidate information.

IMPORTANT DESIGN PRINCIPLE:

The user is the source of truth.

The LLM can:
- analyze
- classify
- summarize
- recommend
- generate proposals

The LLM must NOT silently modify authoritative candidate information.

The database is the source of truth.

New resume versions are proposals until the user approves them.

--------------------------------------------------
CORE USER WORKFLOW
--------------------------------------------------

1. USER ONBOARDING

User provides:

- LinkedIn profile information / permitted LinkedIn access
- GitHub repository links
- at least 3 approved resumes
- Overleaf/LaTeX template/source format
- job preferences
- optional Gmail connection
- optional Google Calendar connection
- optional user-provided LLM API keys

The user owns all factual information.

--------------------------------------------------
2. GITHUB PROJECT UNDERSTANDING
--------------------------------------------------

This is primarily a ONE-TIME onboarding process.

For each GitHub repository:

- read README
- read basic repository metadata
- identify technologies
- identify project purpose
- infer a basic architecture
- generate a concise project summary
- store the structured project summary

Do not repeatedly process GitHub for every job.

Stored project information should include:

- project name
- purpose
- technologies
- architecture summary
- candidate contribution if supported
- repository URL
- evidence/source

Do not invent candidate contributions.

The project understanding layer can be refreshed only when
the user requests it or the repository changes.

--------------------------------------------------
3. CANDIDATE DATABASE
--------------------------------------------------

PostgreSQL is the source of truth.

Core entities:

Candidate
CandidateSkill
Experience
Education
Project
ProjectEvidence
Resume
ResumeVersion
Job
Company
JobRequirement
JobMatch
Application
ApplicationMaterial
FollowUp
EmailInteraction
UserPreference
Evidence

The database should preserve history.

Approved resumes should never be overwritten.

New resume versions are separate records.

--------------------------------------------------
4. AGENT ACCESS TO DATABASE
--------------------------------------------------

Agents must NOT receive unrestricted SQL access.

Expose narrow typed tools/functions.

Examples:

get_candidate_profile()
get_candidate_skills()
get_projects()
get_project(id)
get_resume(id)
get_resume_versions()
get_job(id)
get_application_history()
get_user_preferences()

Proposal/action functions should be separate.

Example:

create_resume_proposal()

A proposal has:

status = PROPOSED

Only after user approval:

status = APPROVED

The LLM must not directly update authoritative candidate facts.

--------------------------------------------------
5. JOB DISCOVERY
--------------------------------------------------

The primary job source is LinkedIn jobs / permitted job data.

The user specifies filters such as:

- AI / GenAI / ML
- entry level
- location
- posted within last 24 hours
- under 10 applicants
- other user-defined filters
- Easy Apply preference

Do not use broad web search unnecessarily.

For company/hiring signals, inspect relevant public posts from
the recent period when available.

If a required field is unavailable:

store UNKNOWN.

Never hallucinate.

For example:

salary not present in JD
=> salary = UNKNOWN

Do NOT estimate salary.

Applicant count not available
=> applicant_count = UNKNOWN

Do NOT guess.

--------------------------------------------------
6. JOB ANALYSIS
--------------------------------------------------

Extract:

- title
- company
- location
- experience level
- required skills
- preferred skills
- responsibilities
- qualifications
- salary if explicitly stated
- applicant count if available
- posting time
- application method
- raw job description

Separate:

REQUIRED
PREFERRED
RESPONSIBILITY
OTHER

Do not allow the LLM to fabricate requirements.

--------------------------------------------------
7. COMPANY INTELLIGENCE
--------------------------------------------------

Use information available from:

- job posting
- company LinkedIn information
- recent relevant company posts
- permitted public company information

The output should contain:

- company name
- role
- short company summary
- role summary
- salary if explicitly available
- location
- company information
- evidence/source for important claims

Distinguish:

VERIFIED
INFERRED
UNKNOWN

The system should prefer UNKNOWN over unsupported inference.

--------------------------------------------------
8. JOB MATCHING
--------------------------------------------------

Compare the JD against the candidate evidence.

The match should NOT be a completely arbitrary LLM score.

Use structured requirement matching.

For each requirement:

SUPPORTED
PARTIALLY_SUPPORTED
NOT_SUPPORTED
UNKNOWN

Calculate a deterministic score from the structured result.

Example:

required skills: 70%
preferred skills: 20%
experience/education: 10%

Exact weights should remain configurable.

The LLM may classify requirement satisfaction,
but deterministic code calculates the final score.

--------------------------------------------------
9. MATCH CATEGORIES
--------------------------------------------------

Strong match:
>70%

Near match:
50-70%

Poor match:
<50%

Strong match:
continue to application preparation.

Near match:
do NOT automatically force a new resume.

Instead show:

"You are close to this role. Your current resumes are not
strongly positioned for this job. Consider creating another
resume direction."

Explain:

- strengths
- missing requirements
- relevant existing projects
- possible resume direction

Poor match:
skip unless the user explicitly chooses otherwise.

--------------------------------------------------
10. RESUME STRATEGY
--------------------------------------------------

The user provides at least 3 approved resumes.

All resumes should follow a standardized Overleaf/LaTeX structure.

The system should first SELECT among existing resumes.

Do NOT unnecessarily rewrite every resume for every job.

Resume selection should consider:

- requirement coverage
- relevant skills
- relevant projects
- relevant experience
- resume specialization

If one existing resume is sufficiently aligned:
use it.

If a job is 50-70% matched and no existing resume is well aligned:
suggest a new resume direction.

--------------------------------------------------
11. RESUME TAILORING
--------------------------------------------------

Tailoring is constrained.

The system may:

- reorder relevant bullets
- choose relevant projects
- emphasize existing skills
- rewrite existing bullets using existing evidence
- modify summary
- remove less relevant content
- create a proposed new resume version

The system must NOT:

- invent skills
- invent experience
- invent projects
- invent metrics
- invent employers
- invent education
- invent dates
- invent achievements

The original approved resume remains unchanged.

Every generated resume is a new version.

The system should generate a .tex proposal using the user's
approved Overleaf template.

The user reviews it.

--------------------------------------------------
12. APPLICATION PACKAGE
--------------------------------------------------

For a qualified job, prepare:

- selected resume
- proposed tailored resume if applicable
- cover letter if needed
- screening answers if needed
- job-specific responses

All generated content must be evidence-grounded.

Store the exact version used for the application.

--------------------------------------------------
13. CRITIC AGENT
--------------------------------------------------

Before application submission, run a separate critic.

The critic should attempt to find:

- unsupported claims
- invented skills
- altered dates
- altered numbers
- incorrect company information
- mismatch with JD
- missing important requirements
- duplicate application
- incomplete application
- inconsistent resume/application information

The critic should output:

PASS
or
FAIL

with structured reasons.

If FAIL:
return to the appropriate generation agent.

Limit revision cycles to prevent infinite loops.

--------------------------------------------------
14. APPLICATION EXECUTION
--------------------------------------------------

The system supports application modes:

PREPARE
APPROVAL_REQUIRED
AUTO_APPLY

PREPARE:
GlassMate prepares the application but the user performs the final
application manually.

APPROVAL_REQUIRED:
GlassMate prepares the application, runs the Critic, and requires
explicit user approval before performing the external action.

AUTO_APPLY:
The user has explicitly enabled automatic application and the target
application mechanism supports compliant automation.

For LinkedIn Easy Apply, do not build prohibited browser
automation or scraping.

The system should prepare the application package and use
a platform-compliant handoff for the final LinkedIn interaction.

Never attempt to bypass platform restrictions.

--------------------------------------------------
15. APPLICATION DATABASE
--------------------------------------------------

Store:

- company
- job
- job URL
- JD snapshot
- match score
- selected resume version
- generated materials
- application timestamp
- source
- status
- follow-up date
- email interactions

Statuses:

DISCOVERED
QUALIFIED
READY
APPLIED
ACKNOWLEDGED
INTERVIEW
REJECTED
WITHDRAWN
NO_RESPONSE

--------------------------------------------------
16. GMAIL
--------------------------------------------------

Optional integration.

Gmail capabilities:

- search relevant application emails
- read relevant threads
- identify application responses
- identify interview invitations
- create drafts
- send emails only according to user permission

For cold outreach:

- identify relevant recent hiring signals
- identify appropriate public recruiting/contact channel
- generate personalized draft
- run critic
- require human approval before sending

Do not mass-email or harvest personal addresses.

--------------------------------------------------
17. GOOGLE CALENDAR
--------------------------------------------------

Optional integration.

When a follow-up is useful:

create a reminder/event.

Before creating:

check whether a relevant reminder already exists.

Do not create unnecessary reminders.

Example:

Applied:
August 25

Follow-up:
September 8

Calendar reminder:
"Follow up with ABC AI regarding GenAI Intern application."

--------------------------------------------------
18. AGENT ARCHITECTURE
--------------------------------------------------

Use specialized agents instead of one giant agent.

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

Use an Orchestrator/Supervisor for workflow control.

The orchestrator should NOT become a giant tool-using LLM.

Deterministic workflow logic should remain in normal application code.

--------------------------------------------------
19. MCP
--------------------------------------------------

Use MCP where it provides a useful tool boundary.

Potential MCP/tool integrations:

- GitHub
- Gmail
- Google Calendar
- controlled candidate/resume/application tools

Do not use MCP unnecessarily for every internal function.

Agents should receive only the tools they need.

Example:

Match Agent:
- get_job
- get_candidate_skills
- get_projects

Resume Agent:
- get_resume
- get_template
- get_projects
- create_resume_proposal

Gmail Agent:
- search_email
- read_thread
- create_draft
- send_email

--------------------------------------------------
20. LLM ROUTING
--------------------------------------------------

The system is free-tier-first.

Do not design around paid inference.

Use a provider abstraction:

LLMProvider
    Gemini
    Groq
    OpenAI
    Anthropic
    other legitimately available providers

The user may provide their own API keys.

The demo can use available free-tier keys.

Do not create accounts or rotate keys to bypass provider
rate limits or terms.

Use cheaper/free models for:

- extraction
- classification
- simple summaries

Use stronger available models for:

- complex job matching
- resume generation
- company synthesis
- critic

Use deterministic code whenever an LLM is unnecessary.

--------------------------------------------------
21. SECURITY
--------------------------------------------------

Never store raw API keys in plaintext.

Use environment variables or secure secret storage.

OAuth tokens must be handled securely.

Gmail permissions should be minimized.

Agents should have least-privilege access.

--------------------------------------------------
22. EVALUATION
--------------------------------------------------

The project must have measurable evaluation.

Job matching:
- precision
- recall
- F1

Requirement classification:
- supported/partial/not-supported accuracy

Resume generation:
- unsupported claim rate
- requirement coverage
- factual consistency
- compilation success

Company intelligence:
- factual accuracy
- source coverage
- unknown handling

Critic:
- false negative rate
- false positive rate

System:
- application preparation time
- human intervention time
- token/API usage
- latency
- successful workflow completion rate

Create a labelled evaluation dataset.

Do not claim success based only on manual demonstrations.

--------------------------------------------------
23. TECHNOLOGY STACK
--------------------------------------------------

Preferred:

Python
FastAPI
PostgreSQL
SQLAlchemy
Pydantic
Docker
LaTeX
MCP
GitHub API/MCP
Gmail API
Google Calendar API
React or lightweight frontend if needed

Use simple technologies where possible.

Do not introduce unnecessary infrastructure.

--------------------------------------------------
24. IMPLEMENTATION PRINCIPLE
--------------------------------------------------

Build incrementally.

Never attempt to implement the entire system in one step.

Each phase must:

1. implement a small feature
2. write tests
3. run tests
4. verify database behavior
5. verify agent outputs
6. commit working code
7. only then proceed

Do not rewrite working components unnecessarily.

--------------------------------------------------
25. DEVELOPMENT STYLE
--------------------------------------------------

Prefer:

- typed Python
- Pydantic schemas
- small services
- dependency injection
- structured LLM outputs
- retries
- logging
- deterministic business logic
- unit tests
- integration tests
- clear agent boundaries

Avoid:

- giant prompts with 50 tools
- unrestricted SQL
- hidden state
- agent loops without limits
- uncontrolled autonomous actions
- storing hallucinated information as truth

--------------------------------------------------
26. PHASE 21 — DEPLOYMENT
--------------------------------------------------

Phase 21 containerizes and operationalizes the existing GlassMate application
through Docker, Docker Compose, CI automation, and environment-based
configuration. The goal is reproducible local development and simple cloud
deployment readiness.

### Objectives

- Backend FastAPI and frontend React are containerized
- Docker Compose orchestrates PostgreSQL, backend, frontend with proper
  networking and service dependencies
- PostgreSQL data persists in a Docker volume
- Alembic migrations run automatically on startup
- Environment variables control all configuration
- CORS is enabled for frontend-backend communication
- Health checks enable readiness monitoring
- GitHub Actions CI validates backend tests and frontend builds
- Application is ready for simple cloud deployment (no Kubernetes/Terraform)
- Documentation guides new developers through local and production setup

### Implementation Requirements

1. **Backend Dockerfile**
   - Use lightweight Python 3.12+ base image
   - Install dependencies from pyproject.toml
   - Expose port 8000
   - Run uvicorn on 0.0.0.0:8000
   - Use environment variables for configuration
   - Include .dockerignore to reduce image size

2. **Frontend Dockerfile**
   - Multi-stage build: compile React/Vite then serve
   - Build stage installs dependencies and runs `npm run build`
   - Production stage uses lightweight Node or static server
   - Accept VITE_API_URL build argument (for backend URL configuration)
   - Expose port 3000
   - Include .dockerignore

3. **Docker Compose**
   - PostgreSQL service with persistent volume
   - Backend service depends_on PostgreSQL (with health checks)
   - Frontend service depends_on Backend
   - Proper service naming for networking
   - Environment variables passed to all services
   - Port mappings for local access
   - Health checks for all services

4. **CORS Configuration**
   - Add CORS middleware to FastAPI
   - Allow frontend to communicate with backend
   - Production should restrict origins (placeholder acceptable for demo)

5. **Environment Configuration**
   - .env.example documents all variables
   - DATABASE_URL works in Docker Compose context
   - VITE_API_URL configures frontend API endpoint
   - POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB configurable
   - ENVIRONMENT separates development from production
   - No hardcoded secrets in Dockerfiles or Compose

6. **Frontend API URL**
   - Frontend code supports configurable API URL (via VITE_API_URL)
   - Defaults to localhost:8000 for development
   - Docker build passes URL at build time

7. **Alembic Migrations**
   - Migrations are source of truth (no Base.metadata.create_all in production)
   - Fresh PostgreSQL database can be initialized via `alembic upgrade head`
   - Migrations are included in backend Docker image
   - Compose setup can run migrations on startup

8. **Health Checks**
   - Backend /health endpoint remains functional
   - Docker health checks confirm service readiness
   - Compose depends_on uses health checks where practical

9. **GitHub Actions CI**
   - Backend job: install dependencies, run pytest, fail if tests fail
   - Frontend job: install dependencies, run build, fail if build fails
   - CI uses PostgreSQL service container for backend tests
   - No secrets or personal API keys required

10. **Documentation**
    - README includes "Quick Start with Docker Compose"
    - README documents environment variables
    - DEVELOPMENT.md documents Phase 21 and deployment procedure
    - PROJECT_SPEC.md includes this Phase 21 specification

### Validation Checklist

Before declaring Phase 21 complete:

- [ ] Backend Dockerfile builds successfully
- [ ] Frontend Dockerfile builds successfully
- [ ] Docker Compose configuration is valid
- [ ] `docker compose up` starts all services
- [ ] PostgreSQL initializes and accepts connections
- [ ] Backend health endpoint responds on http://localhost:8000/health
- [ ] Frontend loads on http://localhost:3000
- [ ] Frontend can fetch from backend
- [ ] Alembic migrations run successfully
- [ ] GitHub Actions CI passes for both backend and frontend
- [ ] No secrets are exposed in code, Dockerfile, or Compose
- [ ] .gitignore excludes .env and Docker artifacts
- [ ] All existing tests still pass
- [ ] No existing functionality is broken

### Non-Goals

- Enterprise DevOps infrastructure
- Kubernetes, ECS, EKS, Helm, Terraform, or similar
- Automated cloud deployment
- Service meshes or advanced monitoring
- Database read replicas or sharding
- Multi-region deployment
- Complex CI/CD orchestration