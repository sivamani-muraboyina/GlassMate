import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import (
    Candidate,
    CandidateSkill,
    Job,
    JobMatch,
    JobRequirement,
    JobRequirementMatch,
    RequirementKind,
    RequirementMatchStatus,
    Resume,
    ResumeVersion,
    ResumeVersionStatus,
)
from app.services.resume_strategy import ResumeStrategyService
import app.models.entities  # noqa: F401


@pytest.fixture
def database() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_strategy_selects_best_approved_resume_and_explains_fit(database: Session) -> None:
    candidate = Candidate(full_name="Candidate")
    candidate.skills = [CandidateSkill(name="Python")]
    job = Job(
        title="Python Engineer",
        source="feed",
        url="https://jobs.example/python",
        fingerprint="strategy-1",
        raw_description="description",
    )
    python = JobRequirement(text="Python", kind=RequirementKind.REQUIRED)
    fastapi = JobRequirement(text="FastAPI", kind=RequirementKind.PREFERRED)
    job.requirements = [python, fastapi]
    general = Resume(
        name="General",
        versions=[ResumeVersion(version_number=1, status=ResumeVersionStatus.APPROVED, tex_content="Python")],
    )
    backend = Resume(
        name="Backend Engineering",
        versions=[
            ResumeVersion(
                version_number=1,
                status=ResumeVersionStatus.APPROVED,
                tex_content="Python FastAPI backend engineering",
            )
        ],
    )
    candidate.resumes = [general, backend]
    session = database
    session.add_all([candidate, job])
    session.commit()
    session.refresh(python)
    session.refresh(fastapi)
    session.add_all(
        [
            JobRequirementMatch(
                job_requirement_id=python.id,
                candidate_id=candidate.id,
                status=RequirementMatchStatus.SUPPORTED,
            ),
            JobRequirementMatch(
                job_requirement_id=fastapi.id,
                candidate_id=candidate.id,
                status=RequirementMatchStatus.PARTIALLY_SUPPORTED,
            ),
            JobMatch(job_id=job.id, candidate_id=candidate.id, score=0.75, category="STRONG_MATCH"),
        ]
    )
    session.commit()

    result = ResumeStrategyService().select_resume(session, job.id, candidate.id)

    assert result.selected_resume_name == "Backend Engineering"
    assert result.selected_version_number == 1
    assert result.selection_score is not None and result.selection_score > 0
    assert result.match_category == "STRONG_MATCH"
    assert result.strengths == ["Python", "FastAPI"]
    assert result.missing_requirements == []


def test_strategy_ignores_proposed_versions(database: Session) -> None:
    candidate = Candidate(full_name="Candidate")
    job = Job(
        title="Engineer",
        source="feed",
        url="https://jobs.example/engineer",
        fingerprint="strategy-2",
        raw_description="description",
    )
    requirement = JobRequirement(text="Python", kind=RequirementKind.REQUIRED)
    job.requirements = [requirement]
    resume = Resume(
        name="General",
        versions=[
            ResumeVersion(version_number=1, status=ResumeVersionStatus.APPROVED, tex_content="Python"),
            ResumeVersion(
                version_number=2,
                status=ResumeVersionStatus.PROPOSED,
                tex_content="Python FastAPI Kubernetes",
            ),
        ],
    )
    candidate.resumes = [resume]
    database.add_all([candidate, job])
    database.commit()

    result = ResumeStrategyService().select_resume(database, job.id, candidate.id)

    assert result.selected_version_number == 1
    assert result.selected_version_id != resume.versions[1].id


def test_strategy_requires_existing_candidate_and_job(database: Session) -> None:
    service = ResumeStrategyService()

    with pytest.raises(LookupError, match="Candidate 999"):
        service.select_resume(database, 1, 999)

    candidate = Candidate(full_name="Candidate")
    database.add(candidate)
    database.commit()
    with pytest.raises(LookupError, match="Job 999"):
        service.select_resume(database, 999, candidate.id)