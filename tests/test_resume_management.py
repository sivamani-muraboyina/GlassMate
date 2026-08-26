import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Candidate, ResumeVersionStatus
from app.schemas.resume import ResumeCreateRequest, ResumeProposalRequest
from app.services.resume_management import ResumeManagementService
import app.models.entities  # noqa: F401


@pytest.fixture
def database() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_resume_versions_preserve_approval_history(database: Session) -> None:
    candidate = Candidate(full_name="Test Candidate")
    database.add(candidate)
    database.commit()
    database.refresh(candidate)
    service = ResumeManagementService()

    resume = service.create_approved_resume(
        database,
        candidate.id,
        ResumeCreateRequest(name="General", tex_content="approved source"),
    )
    proposal = service.create_proposal(
        database,
        candidate.id,
        resume.id,
        ResumeProposalRequest(tex_content="proposed source"),
    )
    approved = service.transition_version(
        database,
        candidate.id,
        resume.id,
        proposal.id,
        ResumeVersionStatus.APPROVED,
    )

    assert resume.versions[0].status == ResumeVersionStatus.APPROVED
    assert resume.versions[0].tex_content == "approved source"
    assert proposal.version_number == 2
    assert proposal.source_version_id == resume.versions[0].id
    assert approved.status == ResumeVersionStatus.APPROVED
    assert approved.tex_content == "proposed source"

    with pytest.raises(ValueError, match="Only proposed"):
        service.transition_version(
            database,
            candidate.id,
            resume.id,
            proposal.id,
            ResumeVersionStatus.REJECTED,
        )


def test_proposal_requires_approved_source_version(database: Session) -> None:
    candidate = Candidate(full_name="Test Candidate")
    database.add(candidate)
    database.commit()
    service = ResumeManagementService()
    resume = service.create_approved_resume(
        database,
        candidate.id,
        ResumeCreateRequest(name="General", tex_content="approved source"),
    )
    proposal = service.create_proposal(
        database,
        candidate.id,
        resume.id,
        ResumeProposalRequest(tex_content="first proposal"),
    )

    with pytest.raises(ValueError, match="approved"):
        service.create_proposal(
            database,
            candidate.id,
            resume.id,
            ResumeProposalRequest(tex_content="second proposal", source_version_id=proposal.id),
        )

    with pytest.raises(LookupError, match="Resume version 999"):
        service.create_proposal(
            database,
            candidate.id,
            resume.id,
            ResumeProposalRequest(tex_content="second proposal", source_version_id=999),
        )


def test_resume_operations_require_candidate_ownership(database: Session) -> None:
    service = ResumeManagementService()
    database.add(Candidate(full_name="Owner"))
    database.commit()

    with pytest.raises(LookupError):
        service.list_resumes(database, 999)
