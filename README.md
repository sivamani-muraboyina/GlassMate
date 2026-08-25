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
frontend work are planned for later phases.

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