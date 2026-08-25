from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Company, Job, RequirementKind
from app.services.job_analysis import JobAnalysisService
import app.models.entities  # noqa: F401


def test_job_analysis_persists_metadata_and_categorized_requirements() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    description = """Experience Level: Entry level
Application Method: External application
Posting Time: 2026-08-25T10:00:00Z

Required:
- Python
- SQL

Preferred:
- FastAPI

Responsibilities:
- Build data pipelines
"""

    with Session(engine) as session:
        company = Company(name="Example Co")
        session.add(company)
        session.flush()
        job = Job(
            company_id=company.id,
            title="Backend Engineer",
            source="feed",
            url="https://jobs.example/backend",
            fingerprint="job-1",
            raw_description=description,
        )
        session.add(job)
        session.commit()
        session.refresh(job)

        analyzed = JobAnalysisService().analyze(session, job.id)

        assert analyzed.experience_level == "Entry level"
        assert analyzed.application_method == "External application"
        assert analyzed.posting_time.replace(tzinfo=timezone.utc) == datetime(
            2026, 8, 25, 10, 0, tzinfo=timezone.utc
        )
        assert analyzed.salary is None
        assert [requirement.kind for requirement in analyzed.requirements] == [
            RequirementKind.REQUIRED,
            RequirementKind.REQUIRED,
            RequirementKind.PREFERRED,
            RequirementKind.RESPONSIBILITY,
        ]
        assert analyzed.requirements[0].text == "Python"


def test_job_analysis_replaces_previous_requirements() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        job = Job(
            title="Analyst",
            source="feed",
            url="https://jobs.example/analyst",
            fingerprint="job-2",
            raw_description="Required:\n- Python",
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        service = JobAnalysisService()

        service.analyze(session, job.id)
        job.raw_description = "Preferred:\n- SQL"
        session.commit()
        analyzed = service.analyze(session, job.id)

        assert len(analyzed.requirements) == 1
        assert analyzed.requirements[0].kind == RequirementKind.PREFERRED
        assert analyzed.requirements[0].text == "SQL"
