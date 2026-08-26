# GlassMate

AI-powered job discovery, evaluation, application preparation,
and career tracking assistant.

## Status

🚧 Under Development

## Goal

GlassMate helps a candidate discover relevant opportunities,
understand their fit, select the appropriate resume, prepare
applications, validate generated content, and track applications
and follow-ups.

## Architecture

Defined in `ARCHITECTURE_DECISIONS.md`.

## Local Setup

Requirements:

- Python 3.12+
- PostgreSQL for database-backed development

Create and activate a virtual environment, then install the project:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

Copy `.env.example` to `.env` and update `DATABASE_URL` for your local
PostgreSQL instance. Start the API with:

```powershell
uvicorn app.main:app --app-dir backend --reload
```

The health endpoint is available at `http://127.0.0.1:8000/health`.

Candidate onboarding is available through:

- `POST /candidates` to save a candidate profile with skills, experience,
  education, and preferences.
- `GET /candidates/{candidate_id}` to retrieve the saved profile.

GitHub project imports are available through:

- `POST /candidates/{candidate_id}/projects/import` to fetch public
    repository metadata, README content, and top-level entries.

Imports are cached by repository content hash and stored with GitHub
source evidence. Repository data does not prove candidate authorship.

Resume management is available through endpoints for registering an
approved resume, listing and retrieving versions, creating proposals,
and explicitly approving or rejecting proposed versions.

Normalized job ingestion is available through `POST /jobs/ingest`.
It computes source fingerprints, reuses duplicate jobs and companies,
and keeps unavailable salary or applicant-count fields as `NULL`.

Structured job analysis is available through `POST /jobs/{job_id}/analyze`.
It extracts explicit metadata and categorizes clearly headed requirements
without inventing missing job information.

Job matching is available through `POST /jobs/{job_id}/matches/{candidate_id}`.
It stores requirement classifications and calculates a deterministic score
using the configured required/preferred weights while excluding `UNKNOWN`.

Company intelligence is available through `POST /jobs/{job_id}/company-intelligence`.
It stores source-labeled company information and role summaries, preferring
`UNKNOWN` when supporting information is unavailable.

Resume strategy is available through `POST /jobs/{job_id}/resume-strategy/{candidate_id}`.
It selects the best approved resume version using deterministic requirement and
candidate-evidence alignment, and explains near-match resume-direction recommendations.

Resume proposals are created through the existing resume version endpoint with
`tex_content` and an optional `source_version_id`. Each proposal records its
approved source version and remains `PROPOSED` until explicitly approved.

Resume versions can be compiled through
`POST /candidates/{candidate_id}/resumes/{resume_id}/versions/{version_id}/compile`.
Compilation runs in a temporary directory with shell escape disabled and returns
structured success, failure, or compiler-unavailable results. Install `pdflatex`
locally to produce PDFs.

Application packages can be prepared through
`POST /candidates/{candidate_id}/jobs/{job_id}/applications`. The endpoint stores
the selected resume version, job snapshot, match score, supplied materials, and
source without submitting to an external platform. An `idempotency_key` makes
retries return the existing package.

Application packages can be reviewed through
`POST /candidates/{candidate_id}/applications/{application_id}/critic`.
The deterministic critic checks resume usability, material claim references,
claim verification, required job coverage, and package completeness, returning
structured `PASS` or `FAIL` findings without mutating the package.

Run the tests with:

```powershell
pytest
```

Phase 0 provides the backend foundation. Phase 1 adds the core database
models and migrations. Phase 2 adds deterministic candidate onboarding.
Phase 3 adds cached GitHub project understanding. Phase 4 adds
immutable resume version management. Agents, external integrations,
and frontend work are planned for later phases. Phase 5 adds
adapter-ready job ingestion and deduplication.
Phase 6 adds structured job analysis. Agents, external integrations, and
frontend work are planned for later phases. Phase 7 adds deterministic job
matching and explainable routing categories. Phase 8 adds source-aware
company intelligence and evidence links. Phase 9 adds deterministic resume
selection and explainable resume strategy recommendations. Phase 10 adds
approved-source resume proposals with provenance. Phase 11 adds sandboxed
deterministic LaTeX compilation checks. Phase 12 adds application package
preparation and job snapshots. Phase 13 adds deterministic critic validation
with structured findings. Phase 14 adds an explicit deterministic workflow
registry with persisted agent-run lifecycle and failure results.
Phase 15 adds a controlled tool registry with agent-scoped access for future
MCP adapters. Phase 16 adds a typed, permission-gated Gmail service boundary
for search, thread reads, drafts, and approved sends. Phase 17 adds a
duplicate-safe Calendar follow-up service boundary. Phase 18 adds a
compliant application execution boundary with approval and handoff safeguards.
Phase 19 adds dependency-free evaluation metrics and a labeled requirement
classification fixture.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- Pydantic
- SQLAlchemy
- MCP
- LLM APIs
- GitHub
- Gmail
- Google Calendar
- LaTeX / Overleaf

## Development

The project is being developed phase-by-phase.
See `PROJECT_SPEC.md`.