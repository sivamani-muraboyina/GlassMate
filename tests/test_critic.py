import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import (
    Application,
    ApplicationMaterial,
    ApplicationStatus,
    Candidate,
    Claim,
    EvidenceStatus,
    Job,
    JobRequirement,
    RequirementKind,
    Resume,
    ResumeVersion,
    ResumeVersionStatus,
)
from app.services.critic import CriticService
import app.models.entities  # noqa: F401


@pytest.fixture
def database() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _application(database: Session, material_claims: list[int] | None = None) -> tuple[Candidate, Application]:
    candidate = Candidate(full_name="Candidate")
    resume = Resume(name="General", candidate=candidate)
    resume.versions = [
        ResumeVersion(
            version_number=1,
            status=ResumeVersionStatus.APPROVED,
            tex_content="approved resume",
        )
    ]
    job = Job(
        title="Engineer",
        source="feed",
        url="https://jobs.example/engineer",
        fingerprint="critic-1",
        raw_description="description",
    )
    database.add_all([candidate, job])
    database.flush()
    application = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_version_id=resume.versions[0].id,
        status=ApplicationStatus.READY,
        job_url_snapshot=job.url,
        jd_snapshot=job.raw_description,
        source=job.source,
        materials=[
            ApplicationMaterial(
                material_type="COVER_LETTER",
                content="letter",
                claims=material_claims or [],
            )
        ],
    )
    database.add(application)
    database.commit()
    database.refresh(application)
    return candidate, application


def test_critic_passes_complete_package(database: Session) -> None:
    candidate, application = _application(database)

    result = CriticService().review(database, candidate.id, application.id)

    assert result.result == "PASS"
    assert result.findings == []


def test_critic_fails_unverified_claim_and_missing_requirement(database: Session) -> None:
    candidate, application = _application(database, material_claims=[999])
    claim = Claim(text="Unverified claim", status=EvidenceStatus.UNKNOWN)
    requirement = JobRequirement(
        job_id=application.job_id,
        text="Kubernetes",
        kind=RequirementKind.REQUIRED,
    )
    database.add_all([claim, requirement])
    database.commit()
    application.materials[0].claims = [claim.id]
    database.commit()

    result = CriticService().review(database, candidate.id, application.id)

    assert result.result == "FAIL"
    assert len(result.findings) == 2
    assert any("not verified" in finding.issue for finding in result.findings)
    assert any("required job requirement" in finding.issue for finding in result.findings)


def test_critic_enforces_candidate_ownership(database: Session) -> None:
    _, application = _application(database)

    with pytest.raises(LookupError, match="Application"):
        CriticService().review(database, 999, application.id)