import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import (
    ApplicationMode,
    ApplicationStatus,
    Candidate,
    Job,
    JobMatch,
    Resume,
    ResumeVersion,
    ResumeVersionStatus,
)
from app.schemas.application import ApplicationMaterialInput, ApplicationPreparationRequest
from app.services.application_preparation import ApplicationPreparationService
import app.models.entities  # noqa: F401


@pytest.fixture
def database() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _setup(database: Session) -> tuple[Candidate, Job, ResumeVersion]:
    candidate = Candidate(full_name="Candidate")
    resume = Resume(name="Backend", candidate=candidate)
    version = ResumeVersion(
        version_number=1,
        status=ResumeVersionStatus.APPROVED,
        tex_content="approved resume",
    )
    resume.versions = [version]
    job = Job(
        title="Engineer",
        source="feed",
        url="https://jobs.example/engineer",
        fingerprint="application-1",
        raw_description="Python requirements",
    )
    database.add_all([candidate, job])
    database.commit()
    database.refresh(candidate)
    database.refresh(job)
    database.refresh(version)
    return candidate, job, version


def test_prepare_application_stores_snapshots_and_materials(database: Session) -> None:
    candidate, job, version = _setup(database)
    database.add(JobMatch(job_id=job.id, candidate_id=candidate.id, score=0.8, category="STRONG_MATCH"))
    database.commit()

    result = ApplicationPreparationService().prepare(
        database,
        candidate.id,
        job.id,
        ApplicationPreparationRequest(
            resume_version_id=version.id,
            mode=ApplicationMode.PREPARE,
            idempotency_key="application-key-1",
            materials=[
                ApplicationMaterialInput(
                    material_type="COVER_LETTER",
                    content="Evidence-grounded letter",
                    claims=[10],
                )
            ],
        ),
    )

    assert result.status == ApplicationStatus.READY
    assert result.job_url_snapshot == job.url
    assert result.jd_snapshot == job.raw_description
    assert result.match_score == 0.8
    assert result.source == "feed"
    assert len(result.materials) == 1
    assert result.materials[0].claims == [10]


def test_prepare_application_is_idempotent(database: Session) -> None:
    candidate, job, version = _setup(database)
    service = ApplicationPreparationService()
    request = ApplicationPreparationRequest(
        resume_version_id=version.id,
        idempotency_key="application-key-2",
    )

    first = service.prepare(database, candidate.id, job.id, request)
    second = service.prepare(database, candidate.id, job.id, request)

    assert second.id == first.id
    assert len(second.materials) == 0

    other_job = Job(
        title="Other Engineer",
        source="feed",
        url="https://jobs.example/other",
        fingerprint="application-2",
        raw_description="other description",
    )
    database.add(other_job)
    database.commit()
    with pytest.raises(ValueError, match="another application"):
        service.prepare(database, candidate.id, other_job.id, request)


def test_prepare_application_rejects_invalid_resume_versions(database: Session) -> None:
    candidate, job, _ = _setup(database)
    rejected = ResumeVersion(
        resume_id=candidate.resumes[0].id,
        version_number=2,
        status=ResumeVersionStatus.REJECTED,
        tex_content="rejected",
    )
    database.add(rejected)
    database.commit()

    with pytest.raises(ValueError, match="approved or proposed"):
        ApplicationPreparationService().prepare(
            database,
            candidate.id,
            job.id,
            ApplicationPreparationRequest(resume_version_id=rejected.id),
        )