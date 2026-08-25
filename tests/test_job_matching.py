from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import (
    Candidate,
    Job,
    JobRequirement,
    RequirementKind,
    RequirementMatchStatus,
)
from app.schemas.job_match import JobMatchRequest, RequirementMatchInput
from app.services.job_matching import JobMatchingService
import app.models.entities  # noqa: F401


def test_job_match_uses_weights_and_excludes_unknown() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        candidate = Candidate(full_name="Candidate")
        job = Job(
            title="Engineer",
            source="feed",
            url="https://jobs.example/engineer",
            fingerprint="job-match-1",
            raw_description="description",
        )
        job.requirements = [
            JobRequirement(text="Python", kind=RequirementKind.REQUIRED),
            JobRequirement(text="FastAPI", kind=RequirementKind.PREFERRED),
            JobRequirement(text="Degree", kind=RequirementKind.REQUIRED),
        ]
        session.add_all([candidate, job])
        session.commit()
        session.refresh(candidate)
        session.refresh(job)
        requirements = {requirement.text: requirement.id for requirement in job.requirements}

        result = JobMatchingService().calculate(
            session,
            job.id,
            candidate.id,
            JobMatchRequest(
                requirements=[
                    RequirementMatchInput(
                        requirement_id=requirements["Python"],
                        status=RequirementMatchStatus.SUPPORTED,
                    ),
                    RequirementMatchInput(
                        requirement_id=requirements["FastAPI"],
                        status=RequirementMatchStatus.PARTIALLY_SUPPORTED,
                    ),
                    RequirementMatchInput(
                        requirement_id=requirements["Degree"],
                        status=RequirementMatchStatus.UNKNOWN,
                    ),
                ]
            ),
        )

        assert result.score == (2.0 + 0.5) / 3
        assert result.category == "STRONG_MATCH"


def test_job_match_returns_unknown_when_no_scoreable_requirements() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        candidate = Candidate(full_name="Candidate")
        job = Job(
            title="Engineer",
            source="feed",
            url="https://jobs.example/engineer-unknown",
            fingerprint="job-match-2",
            raw_description="Required:\n- Python",
        )
        job.requirements = [JobRequirement(text="Python", kind=RequirementKind.REQUIRED)]
        session.add_all([candidate, job])
        session.commit()
        session.refresh(candidate)
        session.refresh(job)

        result = JobMatchingService().calculate(
            session,
            job.id,
            candidate.id,
            JobMatchRequest(
                requirements=[
                    RequirementMatchInput(
                        requirement_id=job.requirements[0].id,
                        status=RequirementMatchStatus.UNKNOWN,
                    )
                ]
            ),
        )

        assert result.score is None
        assert result.category == "UNKNOWN"
