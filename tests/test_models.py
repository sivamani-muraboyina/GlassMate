from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import (
    Application,
    ApplicationMode,
    ApplicationStatus,
    Candidate,
    CandidateSkill,
    Resume,
    ResumeVersion,
    ResumeVersionStatus,
)
import app.models.entities  # noqa: F401


def test_phase_one_metadata_creates_expected_tables() -> None:
    engine = create_engine("sqlite://")

    Base.metadata.create_all(engine)

    assert set(inspect(engine).get_table_names()) == {
        "agent_runs",
        "application_materials",
        "applications",
        "candidate_skills",
        "candidates",
        "claim_evidence",
        "claims",
        "companies",
        "education",
        "email_interactions",
        "evidence",
        "experiences",
        "follow_ups",
        "job_matches",
        "job_requirements",
        "job_requirement_matches",
        "jobs",
        "project_evidence",
        "projects",
        "resume_versions",
        "resumes",
        "user_preferences",
    }


def test_candidate_resume_and_application_defaults() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        candidate = Candidate(full_name="Test Candidate")
        resume = Resume(name="General", candidate=candidate)
        version = ResumeVersion(version_number=1, tex_content="% test", resume=resume)
        application = Application(
            job_id=1,
            candidate_id=1,
            mode=ApplicationMode.PREPARE,
            status=ApplicationStatus.DISCOVERED,
        )
        session.add_all([candidate, version, application])
        session.commit()
        session.refresh(version)
        session.refresh(application)

        assert version.status == ResumeVersionStatus.PROPOSED
        assert application.mode == ApplicationMode.PREPARE
        assert application.status == ApplicationStatus.DISCOVERED


def test_candidate_skills_are_unique_per_candidate() -> None:
    constraint = next(
        constraint
        for constraint in CandidateSkill.__table__.constraints
        if constraint.name == "uq_candidate_skills_candidate_name"
    )

    assert {column.name for column in constraint.columns} == {"candidate_id", "name"}
