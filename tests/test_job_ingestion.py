from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Company, Job
from app.schemas.job import JobIngestionRequest
from app.services.job_ingestion import JobIngestionService
import app.models.entities  # noqa: F401


def test_job_ingestion_deduplicates_and_preserves_unknown_fields() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    request = JobIngestionRequest(
        source="permitted_feed",
        title="AI Engineer",
        company_name="Glass Labs",
        url="https://jobs.example/ai-engineer",
        raw_description="Build AI systems.",
    )

    with Session(engine) as session:
        service = JobIngestionService()
        job, ingested = service.ingest(session, request)
        duplicate, ingested_again = service.ingest(session, request)

        assert ingested is True
        assert ingested_again is False
        assert job.id == duplicate.id
        assert job.salary is None
        assert job.applicant_count is None
        assert len(job.fingerprint) == 64
        assert session.query(Job).count() == 1
        assert session.query(Company).count() == 1


def test_explicit_fingerprint_is_used() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    request = JobIngestionRequest(
        source="feed",
        title="Data Engineer",
        company_name="Example Co",
        url="https://jobs.example/data",
        raw_description="Work with data.",
        fingerprint="source-specific-id",
    )

    with Session(engine) as session:
        job, _ = JobIngestionService().ingest(session, request)

    assert job.fingerprint == "source-specific-id"
