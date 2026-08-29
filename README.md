# GlassMate

> An AI-powered career assistant that analyzes job requirements, matches them against candidate evidence, prepares evidence-backed application materials, and guides intelligent application workflows.

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Latest-61DAFB?logo=react)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)](https://www.docker.com/)
[![pytest](https://img.shields.io/badge/pytest-53%2F53-brightgreen)](https://pytest.org/)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue?logo=github)](https://github.com/features/actions)

---

## 🎯 The Problem

Job hunting is fragmented and error-prone:

- **Information overload**: Candidates discover jobs but struggle to evaluate genuine fit
- **Manual tailoring**: Preparing tailored applications for each opportunity is time-consuming
- **Trust and accuracy**: AI-generated resume claims can hallucinate; separating evidence-backed facts from proposals is difficult
- **Workflow fragmentation**: Job discovery, application tracking, and follow-ups become siloed
- **Verification gap**: Determining whether a candidate truly matches a job description requires semantic understanding, contextual reasoning, and verification against actual evidence

GlassMate solves this by coupling **deterministic structure** with **targeted AI reasoning**, keeping the candidate in control of what gets said about them.

---

## 🚀 What is GlassMate?

GlassMate is a complete backend application + interactive frontend that:

1. **Ingests candidate evidence** — skills, experience, education, GitHub projects, and approved resumes
2. **Discovers and analyzes jobs** — extracts structured job requirements from listings
3. **Performs deterministic matching** — calculates candidate-to-job fit without inventing missing information
4. **Applies AI strategically** — uses LLM agents for semantic reasoning (job analysis, company intelligence, resume strategy) while keeping deterministic matching and human approval boundaries rigid
5. **Generates evidence-backed materials** — creates resume proposals grounded in candidate's actual experience
6. **Validates output** — independent critic agent checks resume completeness, requirement coverage, and factual consistency
7. **Tracks applications** — records job snapshots, application status, and follow-ups
8. **Integrates workflow tools** — optional Gmail, Calendar, and platform-specific application execution (with human approval)

**What it is NOT:**
- A generic chatbot
- A simple RAG wrapper around job data
- An automated LinkedIn scraper
- A tool that invents candidate experience or skills

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend (Phase 20)                │
│                  Candidate Dashboard & Workflow UI              │
│              (Readiness, Job Matching, Resume Strategy)        │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/REST
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    FastAPI Backend (Phases 1-19+21)             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Layer (Routes)                                      │  │
│  │  /health, /candidates, /jobs, /matches, /applications   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  Orchestrator (Deterministic Workflow Registry)          │  │
│  │  - Workflow lifecycle management                         │  │
│  │  - Agent execution coordination                          │  │
│  │  - Agent run persistence                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  Services Layer (Deterministic + LLM)                    │  │
│  │                                                          │  │
│  │  Deterministic:                                          │  │
│  │  ├─ CandidateOnboarding (validation, persistence)       │  │
│  │  ├─ JobIngestion (deduplication, normalization)         │  │
│  │  ├─ JobMatching (scoring, classification)               │  │
│  │  ├─ ResumeManagement (versioning, immutability)         │  │
│  │  ├─ ApplicationPreparation (packaging, snapshots)        │  │
│  │  └─ LaTeX Compilation (sandboxed, deterministic)        │  │
│  │                                                          │  │
│  │  LLM Agent-Based:                                        │  │
│  │  ├─ JobAnalysis (requirement extraction)                │  │
│  │  ├─ ProjectIntelligence (GitHub understanding)          │  │
│  │  ├─ CompanyIntelligence (structured synthesis)          │  │
│  │  ├─ ResumeStrategy (proposal generation)                │  │
│  │  ├─ Critic (validation & verification)                  │  │
│  │  ├─ Gmail (email management)                            │  │
│  │  └─ Calendar (follow-up scheduling)                     │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  Tool/MCP Layer (Agent-Scoped Tool Access)               │  │
│  │  ├─ GitHub API (public repository data)                  │  │
│  │  ├─ Gmail API (search, read, draft, send)                │  │
│  │  ├─ Google Calendar API (event creation)                 │  │
│  │  └─ LLM Provider Abstraction                             │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │ Database
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│       PostgreSQL (Phase 1)  +  Alembic Migrations (Phase 21)    │
│                                                                 │
│  Entities:                                                      │
│  ├─ Candidate (profile, skills, experience, education)        │
│  ├─ Evidence (grounded claims for verification)               │
│  ├─ Project (GitHub repos with architecture, technologies)    │
│  ├─ Resume (immutable approved versions + proposals)          │
│  ├─ Job (deduplicated, normalized job postings)               │
│  ├─ JobMatch (requirement classifications + scores)          │
│  ├─ Application (prepared materials, snapshots, status)       │
│  ├─ Company (verified/inferred/unknown intelligence)          │
│  └─ AgentRun (workflow execution lifecycle)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

See [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) for the complete list. Highlights:

| Decision | Rationale |
|----------|-----------|
| **Interface-first design** | API contracts defined before implementation ensures clear boundaries |
| **Deterministic matching** | Job fit scored via rules, not LLM opinion, ensuring reproducibility |
| **Evidence-grounded claims** | Every candidate fact ties back to source (resume, project, profile) |
| **Three-value information** | NULL ≠ UNKNOWN ≠ NOT_SUPPORTED (explicit missing-data handling) |
| **Human approval boundaries** | LLM generates proposals; user approves before persistence |
| **Agent-scoped tools** | Agents only access tools they need (principle of least privilege) |
| **Source-aware data** | Company info tagged as VERIFIED/INFERRED/UNKNOWN; no hallucination |
| **Immutable approved resumes** | Once approved, resume versions never change (audit trail) |
| **Idempotent external actions** | Application submissions, email sends use idempotency keys |

---

## 🔄 Application Flow

```
1. CANDIDATE ONBOARDING
   ├─ Provide profile (name, email, skills, experience, education)
   ├─ Upload GitHub repositories → cached project understanding
   ├─ Upload approved resumes (≥3 versions)
   └─ Set job preferences

2. JOB DISCOVERY & ANALYSIS
   ├─ Ingest job postings
   ├─ LLM: Extract structured requirements (required/preferred/responsibility)
   ├─ Deterministic: Deduplicate and normalize jobs
   └─ Deterministic: Store company info (fingerprint-based dedup)

3. JOB MATCHING
   ├─ For each job:
   │  ├─ LLM: Semantic analysis of job requirements vs candidate skills
   │  ├─ Deterministic: Classify each requirement (SUPPORTED/PARTIAL/NOT/UNKNOWN)
   │  ├─ Deterministic: Calculate match score (weighted by required/preferred)
   │  └─ Route to category (STRONG_MATCH / NEAR_MATCH / POOR_MATCH)
   └─ Store match record with classifications

4. INTELLIGENCE GATHERING
   ├─ LLM: Analyze company from job listing and public signals
   ├─ LLM: Summarize company, role, hiring signals
   └─ Deterministic: Tag company info as VERIFIED/INFERRED/UNKNOWN

5. RESUME STRATEGY
   ├─ For a qualified job:
   │  ├─ Deterministic: Identify best approved resume version
   │  ├─ LLM: Propose targeted resume direction for this specific job
   │  ├─ LLM: Generate new resume version proposal (if needed)
   │  └─ Deterministic: Store proposal with PROPOSED status
   └─ User reviews and approves/rejects proposal

6. APPLICATION PREPARATION
   ├─ User selects job and approved resume
   ├─ Deterministic: Package materials (resume, job snapshot, match score)
   ├─ Deterministic: Capture application mode (PREPARE/APPROVAL_REQUIRED/AUTO_APPLY)
   └─ Deterministic: Create immutable application record

7. VALIDATION
   ├─ LLM (Critic): Check resume completeness vs job requirements
   ├─ LLM (Critic): Verify claims against candidate evidence
   ├─ LLM (Critic): Detect unsupported or hallucinated content
   └─ Return structured findings (PASS / FAIL with explanations)

8. APPLICATION SUBMISSION
   ├─ For PREPARE mode: User submits manually
   ├─ For APPROVAL_REQUIRED: Show package, require user approval before submit
   ├─ For AUTO_APPLY: Execute automated application (platform-specific)
   └─ Record application timestamp and status

9. TRACKING & FOLLOW-UP
   ├─ Track application status (DISCOVERED→APPLIED→INTERVIEW→etc.)
   ├─ Optional: Calendar reminders for follow-ups
   ├─ Optional: Gmail monitoring for recruiter responses
   └─ Maintain audit trail of all changes
```

---

## 📊 Current Implementation Status

| Phase | Feature | Status |
|-------|---------|--------|
| **0** | Project Foundation | ✅ Complete |
| **1** | Database Schema & Migrations | ✅ Complete |
| **2** | Candidate Onboarding | ✅ Complete |
| **3** | GitHub Project Intelligence | ✅ Complete |
| **4** | Resume Management | ✅ Complete |
| **5** | Job Ingestion | ✅ Complete |
| **6** | Job Analysis | ✅ Complete |
| **7** | Job Matching | ✅ Complete |
| **8** | Company Intelligence | ✅ Complete |
| **9** | Resume Strategy | ✅ Complete |
| **10** | Resume Proposals | ✅ Complete |
| **11** | LaTeX Compilation | ✅ Complete |
| **12** | Application Preparation | ✅ Complete |
| **13** | Critic Validation | ✅ Complete |
| **14** | Orchestration | ✅ Complete |
| **15** | MCP / Tool Abstraction | ✅ Complete |
| **16** | Gmail Integration | ✅ Complete |
| **17** | Calendar Integration | ✅ Complete |
| **18** | Application Execution | ✅ Complete |
| **19** | Evaluation Metrics | ✅ Complete |
| **20** | React Frontend | ✅ Complete |
| **21** | Docker Deployment | ✅ Complete |

---

## 🎛️ Features

### Candidate Intelligence
- ✅ Profile management (skills, experience, education)
- ✅ GitHub project discovery and understanding (cached, one-time)
- ✅ Evidence linking (tie candidate claims to sources)
- ✅ Approved resume versioning (immutable history)

### Job Matching
- ✅ Structured job analysis (requirements extracted by LLM)
- ✅ Deterministic matching (SUPPORTED/PARTIALLY/NOT/UNKNOWN classification)
- ✅ Score calculation (weighted by required vs preferred)
- ✅ Three-tier categorization (STRONG/NEAR/POOR match)

### Resume & Application Preparation
- ✅ Resume version management (approved + proposed)
- ✅ LLM-powered resume strategy (tailored recommendations)
- ✅ LaTeX compilation (sandboxed, deterministic)
- ✅ Application material packaging (resume + job snapshot)

### Validation & Guardrails
- ✅ Critic agent (independent validation, max 3 revisions)
- ✅ Evidence grounding (no hallucinated claims)
- ✅ Requirement coverage checking
- ✅ Factual consistency verification

### Integrations
- ✅ GitHub API (public repository data)
- ✅ Gmail (search, read threads, create drafts, send emails)
- ✅ Google Calendar (schedule follow-ups)
- ✅ LLM provider abstraction (multiple model support)

### Deployment & Operations
- ✅ Docker containerization (backend + frontend)
- ✅ Docker Compose orchestration (PostgreSQL + services)
- ✅ Health checks and readiness probes
- ✅ GitHub Actions CI (backend tests + frontend build)
- ✅ Environment-based configuration

### User Interface
- ✅ React dashboard (candidate readiness, job matches, resume status, applications)
- ✅ Real-time backend integration
- ✅ Dark/light theme
- ✅ Responsive design

---

## 🚀 Quick Start

### With Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/sivamani-muraboyina/GlassMate.git
cd GlassMate

# Copy environment configuration
cp .env.example .env

# Start all services (PostgreSQL, backend, frontend)
docker compose up

# In another terminal, run database migrations
docker compose exec backend alembic upgrade head
```

Then open your browser:

- **Frontend**: http://localhost:3000
- **Backend health**: http://localhost:8000/health
- **API docs**: http://localhost:8000/docs (Swagger)

### Local Development (Without Docker)

**Prerequisites:**

- Python 3.12+
- PostgreSQL 16+
- Node.js 24+

**Backend:**

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -e ".[test]"

# Create .env from template
cp .env.example .env

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --app-dir backend --reload
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Then open http://localhost:5173.

---

## 📋 API Overview

### Core Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Service health check |
| **Candidate** | | |
| POST | `/candidates` | Create candidate profile |
| GET | `/candidates/{id}` | Retrieve candidate profile |
| POST | `/candidates/{id}/projects/import` | Import GitHub project |
| **Resume** | | |
| POST | `/candidates/{id}/resumes` | Create approved resume |
| GET | `/candidates/{id}/resumes` | List resumes |
| POST | `/candidates/{id}/resumes/{rid}/versions` | Create resume proposal |
| **Jobs** | | |
| POST | `/jobs/ingest` | Ingest job posting |
| POST | `/jobs/{id}/analyze` | Analyze job requirements |
| POST | `/jobs/{id}/matches/{cid}` | Calculate job-candidate match |
| POST | `/jobs/{id}/company-intelligence` | Analyze company |
| **Applications** | | |
| POST | `/candidates/{cid}/jobs/{jid}/applications` | Prepare application |
| POST | `/candidates/{cid}/applications/{aid}/critic` | Validate materials |
| POST | `/candidates/{cid}/applications/{aid}/execute` | Submit application |

**Full API Documentation:** Available at `/docs` (Swagger UI) when backend is running.

---

## 🗄️ Data Model

### Core Entities

**Candidate**
- Profile (name, email)
- Skills (with proficiency levels)
- Experience (employer, title, dates, description)
- Education (institution, degree, field)

**Evidence**
- Source type (GitHub, resume, profile, etc.)
- Content and metadata
- Status (VERIFIED / INFERRED / UNKNOWN)

**Project**
- Repository URL, name, purpose
- Technologies, architecture summary
- Candidate contribution claim (grounded in evidence, not assumed)

**Resume**
- Multiple versions with immutable approved originals
- Versions tagged as PROPOSED / APPROVED / REJECTED
- LaTeX and plain-text content

**Job**
- Normalized posting with deduplication
- Requirements classified as REQUIRED / PREFERRED / RESPONSIBILITY / OTHER
- Source information for audit

**JobMatch**
- Classification of each requirement (SUPPORTED/PARTIAL/NOT/UNKNOWN)
- Deterministic score (0-100)
- Match category (STRONG/NEAR/POOR)

**Application**
- Resume version used
- Job snapshot (frozen at time of application)
- Match score and requirement summary
- Application mode and status

---

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest -v

# Specific test file
pytest tests/test_job_matching.py -v

# With coverage
pytest --cov=backend/app tests/
```

**Test Coverage:**

- ✅ **59 tests** covering:
  - Backend foundation & configuration
  - Database models & migrations
  - Candidate onboarding workflows
  - Job analysis & matching
  - Resume management & proposals
  - Company intelligence
  - Application preparation
  - Critic validation
  - GitHub integration
  - Gmail operations
  - Calendar scheduling
  - LaTeX compilation
  - Interface contracts

- ✅ **53/53 tests passing** (as of Phase 21)

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React, Vite | User-facing dashboard and workflows |
| **Backend** | FastAPI, Uvicorn | REST API, request handling, lifespan management |
| **ORM** | SQLAlchemy 2.0+ | Type-safe database object mapping |
| **Migrations** | Alembic | Schema versioning and evolution |
| **Database** | PostgreSQL 16+ | Persistent data storage |
| **Validation** | Pydantic | Request/response schema validation |
| **AI/LLM** | LLM provider abstraction | Model-agnostic reasoning (OpenAI, Anthropic, etc.) |
| **Orchestration** | Python deterministic workflows | Agent coordination and tool routing |
| **Containers** | Docker, Docker Compose | Reproducible local/cloud deployment |
| **CI** | GitHub Actions | Automated testing and validation |
| **Testing** | pytest, httpx | Unit and integration tests |

---

## 🔐 Security & Guardrails

- **Evidence grounding**: Candidate claims linked to verified sources (no hallucination)
- **Human approval**: LLM outputs reviewed/approved before persistence
- **Three-value logic**: Explicit handling of NULL / UNKNOWN / NOT_SUPPORTED
- **Tool scoping**: Agents receive only necessary permissions (ToolRegistry)
- **Immutable records**: Approved resumes, applications never retroactively changed
- **Idempotency**: External actions (email, calendar, applications) use idempotency keys
- **Environment-based config**: Secrets via .env, never hard-coded
- **Source tracking**: All data tagged with source (VERIFIED/INFERRED/UNKNOWN)

---

## 📚 Architecture Diagrams

See `docs/` for detailed architectural diagrams:
- `docs/architecture.svg` — System component overview
- `docs/application_flow.svg` — End-to-end workflow
- `docs/deployment.svg` — Docker/cloud deployment
- `docs/data_model.svg` — Database entity relationships

---

## 🚢 Deployment

### Local (Docker Compose)

```bash
docker compose up
docker compose exec backend alembic upgrade head
# Frontend at http://localhost:3000
# Backend at http://localhost:8000
```

### Cloud Deployment (Ready)

GlassMate is containerized and environment-driven, making it ready for:
- Railway
- Render
- DigitalOcean App Platform
- AWS ECS/Fargate (via Docker)
- Any container orchestration platform

**Deployment checklist:**
- ✅ Backend & frontend containerized
- ✅ All config via environment variables
- ✅ Alembic migrations included in container
- ✅ Health checks configured
- ✅ Secrets management via .env / platform secrets
- ✅ CI/CD pipeline ready (GitHub Actions)

---

## 📖 Documentation

- **[ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md)** — 22 key architectural decisions
- **[DEVELOPMENT.md](DEVELOPMENT.md)** — Phase-by-phase build progress (21 phases)
- **[PROJECT_SPEC.md](PROJECT_SPEC.md)** — Detailed requirements and specifications
- **API Docs** — Swagger UI at `/docs` when backend is running

---

## 🎓 Learning Path

If you're reviewing GlassMate for hiring/evaluation:

1. **Start here**: [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) (5 min)
   - Understand core design principles

2. **Explore the flow**: This README's "Application Flow" section (5 min)
   - See how deterministic + LLM logic separates

3. **Read the models**: [backend/app/models/entities.py](backend/app/models/entities.py) (10 min)
   - Understand data persistence strategy

4. **Explore a service**: [backend/app/services/job_matching.py](backend/app/services/job_matching.py) (10 min)
   - See deterministic logic in action

5. **Run the tests**: `pytest -v` (2 min)
   - Verify functionality

6. **Start locally**: Follow "Quick Start" above (5 min)
   - See the dashboard

---

## 🤔 Why GlassMate?

Most "AI job assistant" projects are thin wrappers around LLM APIs. GlassMate is different:

### Engineering Rigor
- **21 phases of incremental development** — Each phase small, testable, complete
- **53 passing tests** — Validation beyond "it looked good in a demo"
- **Evidence-grounded design** — No hallucination; all claims tie to sources
- **Clear separation of concerns** — Deterministic vs LLM logic explicitly divided

### Architectural Maturity
- **Interface-first design** — API contracts defined before implementation
- **Service abstraction** — Each responsibility has a clear boundary
- **Tool scoping** — Agents receive only the permissions they need
- **Workflow registry** — Explicit orchestration, not ad-hoc LLM loops

### Production Readiness
- **Full containerization** — Ready for Cloud deployment
- **Database migrations** — Schema evolution managed with Alembic
- **Health checks** — Readiness monitoring built in
- **CI/CD** — GitHub Actions validates every change

### Honest About Limitations
- No LinkedIn scraping automation
- No CAPTCHA bypass
- No unrestricted browser automation
- Platform-compliant integrations only

---

## 📝 Known Limitations

- **OAuth setup required**: Gmail and Calendar require user OAuth setup (not automatic)
- **Model abstraction**: LLM provider abstraction layer defined but currently demonstrates with one provider
- **Platform limitations**: Auto-apply limited to platforms with clear API contracts
- **LaTeX requirement**: PDF generation requires `pdflatex` on host system
- **Email drafting**: Gmail creates drafts; user must approve before send (by design)
- **No LinkedIn automation**: Compliant with platform terms; application flow requires human approval

---

## 🤝 Contributing

This is a portfolio project. The codebase demonstrates:
- Clean architecture
- Engineering discipline
- Test-driven development
- Evidence-grounded design
- Thoughtful API design

If you'd like to extend GlassMate:

1. Inspect the architecture ([ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md))
2. Follow the phase discipline ([DEVELOPMENT.md](DEVELOPMENT.md))
3. Write tests first
4. Maintain separation of deterministic and LLM logic
5. Keep evidence grounding intact

---

## 📄 License

[Specify your license here - MIT, Apache 2.0, etc.]

---

## 👤 Author

**Created by:** [Your Name]  
**GitHub:** [@sivamani-muraboyina](https://github.com/sivamani-muraboyina)  
**Repository:** [GlassMate](https://github.com/sivamani-muraboyina/GlassMate)

---

## 🙏 Acknowledgments

Built as a portfolio project demonstrating:
- Full-stack AI system design
- Backend architecture and database design
- Frontend integration with complex backend
- Testing and validation
- Deployment and DevOps
- LLM agent orchestration
- Evidence-grounded AI