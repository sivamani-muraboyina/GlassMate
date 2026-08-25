from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EvidenceStatus(StrEnum):
    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class RequirementKind(StrEnum):
    REQUIRED = "REQUIRED"
    PREFERRED = "PREFERRED"
    RESPONSIBILITY = "RESPONSIBILITY"
    OTHER = "OTHER"


class RequirementMatchStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    UNKNOWN = "UNKNOWN"


class ResumeVersionStatus(StrEnum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApplicationMode(StrEnum):
    PREPARE = "PREPARE"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    AUTO_APPLY = "AUTO_APPLY"


class ApplicationStatus(StrEnum):
    DISCOVERED = "DISCOVERED"
    QUALIFIED = "QUALIFIED"
    READY = "READY"
    APPLIED = "APPLIED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INTERVIEW = "INTERVIEW"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    NO_RESPONSE = "NO_RESPONSE"


class AgentRunStatus(StrEnum):
    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Candidate(TimestampMixin, Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(320), unique=True)

    skills: Mapped[list["CandidateSkill"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")
    experiences: Mapped[list["Experience"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")
    education: Mapped[list["Education"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")
    resumes: Mapped[list["Resume"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")
    preferences: Mapped["UserPreference | None"] = relationship(back_populates="candidate", uselist=False, cascade="all, delete-orphan")


class CandidateSkill(Base, TimestampMixin):
    __tablename__ = "candidate_skills"
    __table_args__ = (UniqueConstraint("candidate_id", "name", name="uq_candidate_skills_candidate_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120))
    proficiency: Mapped[str | None] = mapped_column(String(50))

    candidate: Mapped[Candidate] = relationship(back_populates="skills")


class Experience(Base, TimestampMixin):
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"))
    employer: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    candidate: Mapped[Candidate] = relationship(back_populates="experiences")


class Education(Base, TimestampMixin):
    __tablename__ = "education"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"))
    institution: Mapped[str] = mapped_column(String(200))
    degree: Mapped[str | None] = mapped_column(String(200))
    field_of_study: Mapped[str | None] = mapped_column(String(200))

    candidate: Mapped[Candidate] = relationship(back_populates="education")


class Evidence(Base, TimestampMixin):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_type: Mapped[str] = mapped_column(String(50))
    source_uri: Mapped[str | None] = mapped_column(String(1000))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[EvidenceStatus] = mapped_column(Enum(EvidenceStatus), default=EvidenceStatus.UNKNOWN)

    claims: Mapped[list["ClaimEvidence"]] = relationship(back_populates="evidence")


class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("candidate_id", "repository_url"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    purpose: Mapped[str | None] = mapped_column(Text)
    technologies: Mapped[list[str]] = mapped_column(JSON, default=list)
    architecture_summary: Mapped[str | None] = mapped_column(Text)
    candidate_contribution: Mapped[str | None] = mapped_column(Text)
    repository_url: Mapped[str] = mapped_column(String(1000))
    content_hash: Mapped[str | None] = mapped_column(String(128))

    candidate: Mapped[Candidate] = relationship(back_populates="projects")
    evidence: Mapped[list["ProjectEvidence"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectEvidence(Base):
    __tablename__ = "project_evidence"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    evidence_id: Mapped[int] = mapped_column(ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True)

    project: Mapped[Project] = relationship(back_populates="evidence")
    evidence: Mapped[Evidence] = relationship()


class Claim(Base, TimestampMixin):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    status: Mapped[EvidenceStatus] = mapped_column(Enum(EvidenceStatus), default=EvidenceStatus.UNKNOWN)

    evidence: Mapped[list["ClaimEvidence"]] = relationship(back_populates="claim", cascade="all, delete-orphan")


class ClaimEvidence(Base):
    __tablename__ = "claim_evidence"

    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id", ondelete="CASCADE"), primary_key=True)
    evidence_id: Mapped[int] = mapped_column(ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True)

    claim: Mapped[Claim] = relationship(back_populates="evidence")
    evidence: Mapped[Evidence] = relationship(back_populates="claims")


class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    template_source: Mapped[str | None] = mapped_column(Text)

    candidate: Mapped[Candidate] = relationship(back_populates="resumes")
    versions: Mapped[list["ResumeVersion"]] = relationship(back_populates="resume", cascade="all, delete-orphan")


class ResumeVersion(Base, TimestampMixin):
    __tablename__ = "resume_versions"
    __table_args__ = (UniqueConstraint("resume_id", "version_number", name="uq_resume_versions_resume_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"))
    version_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[ResumeVersionStatus] = mapped_column(Enum(ResumeVersionStatus), default=ResumeVersionStatus.PROPOSED)
    tex_content: Mapped[str] = mapped_column(Text)

    resume: Mapped[Resume] = relationship(back_populates="versions")


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300), unique=True)
    summary: Mapped[str | None] = mapped_column(Text)
    information_status: Mapped[EvidenceStatus] = mapped_column(Enum(EvidenceStatus), default=EvidenceStatus.UNKNOWN)

    jobs: Mapped[list["Job"]] = relationship(back_populates="company")


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("source", "fingerprint"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))
    title: Mapped[str] = mapped_column(String(300))
    location: Mapped[str | None] = mapped_column(String(300))
    source: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(1000))
    fingerprint: Mapped[str] = mapped_column(String(128))
    raw_description: Mapped[str] = mapped_column(Text)
    salary: Mapped[str | None] = mapped_column(String(200))
    applicant_count: Mapped[int | None] = mapped_column(Integer)
    experience_level: Mapped[str | None] = mapped_column(String(100))
    posting_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    application_method: Mapped[str | None] = mapped_column(String(200))

    company: Mapped[Company | None] = relationship(back_populates="jobs")
    requirements: Mapped[list["JobRequirement"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    matches: Mapped[list["JobMatch"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class JobRequirement(Base, TimestampMixin):
    __tablename__ = "job_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text)
    kind: Mapped[RequirementKind] = mapped_column(Enum(RequirementKind))

    job: Mapped[Job] = relationship(back_populates="requirements")
    matches: Mapped[list["JobRequirementMatch"]] = relationship(
        back_populates="requirement", cascade="all, delete-orphan"
    )


class JobRequirementMatch(Base, TimestampMixin):
    __tablename__ = "job_requirement_matches"
    __table_args__ = (UniqueConstraint("job_requirement_id", "candidate_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    job_requirement_id: Mapped[int] = mapped_column(ForeignKey("job_requirements.id", ondelete="CASCADE"))
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"))
    status: Mapped[RequirementMatchStatus] = mapped_column(Enum(RequirementMatchStatus))

    requirement: Mapped[JobRequirement] = relationship(back_populates="matches")


class JobMatch(Base, TimestampMixin):
    __tablename__ = "job_matches"
    __table_args__ = (UniqueConstraint("job_id", "candidate_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"))
    score: Mapped[float | None]
    category: Mapped[str | None] = mapped_column(String(50))

    job: Mapped[Job] = relationship(back_populates="matches")


class Application(Base, TimestampMixin):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    resume_version_id: Mapped[int | None] = mapped_column(ForeignKey("resume_versions.id"))
    mode: Mapped[ApplicationMode] = mapped_column(Enum(ApplicationMode), default=ApplicationMode.PREPARE)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), default=ApplicationStatus.DISCOVERED)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    idempotency_key: Mapped[str | None] = mapped_column(String(200), unique=True)

    materials: Mapped[list["ApplicationMaterial"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    follow_ups: Mapped[list["FollowUp"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    email_interactions: Mapped[list["EmailInteraction"]] = relationship(back_populates="application", cascade="all, delete-orphan")


class ApplicationMaterial(Base, TimestampMixin):
    __tablename__ = "application_materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"))
    material_type: Mapped[str] = mapped_column(String(80))
    content: Mapped[str] = mapped_column(Text)
    claims: Mapped[list[int]] = mapped_column(JSON, default=list)

    application: Mapped[Application] = relationship(back_populates="materials")


class FollowUp(Base, TimestampMixin):
    __tablename__ = "follow_ups"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"))
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_event_id: Mapped[str | None] = mapped_column(String(300), unique=True)

    application: Mapped[Application] = relationship(back_populates="follow_ups")


class EmailInteraction(Base, TimestampMixin):
    __tablename__ = "email_interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"))
    provider_message_id: Mapped[str] = mapped_column(String(300), unique=True)
    subject: Mapped[str | None] = mapped_column(String(500))
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    application: Mapped[Application] = relationship(back_populates="email_interactions")


class UserPreference(Base, TimestampMixin):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), unique=True)
    preferences: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)

    candidate: Mapped[Candidate] = relationship(back_populates="preferences")


class AgentRun(Base, TimestampMixin):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_name: Mapped[str] = mapped_column(String(100))
    workflow_name: Mapped[str] = mapped_column(String(150))
    status: Mapped[AgentRunStatus] = mapped_column(Enum(AgentRunStatus), default=AgentRunStatus.STARTED)
    input_data: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    output_data: Mapped[dict[str, object] | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
