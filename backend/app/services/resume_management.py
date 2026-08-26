from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Candidate, Resume, ResumeVersion, ResumeVersionStatus
from app.schemas.resume import ResumeCreateRequest, ResumeProposalRequest


class ResumeManagementService:
    def create_approved_resume(
        self, session: Session, candidate_id: int, request: ResumeCreateRequest
    ) -> Resume:
        if session.get(Candidate, candidate_id) is None:
            raise LookupError(f"Candidate {candidate_id} was not found")
        resume = Resume(
            candidate_id=candidate_id,
            name=request.name,
            template_source=request.template_source,
        )
        resume.versions = [
            ResumeVersion(
                version_number=1,
                status=ResumeVersionStatus.APPROVED,
                tex_content=request.tex_content,
            )
        ]
        session.add(resume)
        session.commit()
        return self.get_resume(session, candidate_id, resume.id)

    def create_proposal(
        self, session: Session, candidate_id: int, resume_id: int, request: ResumeProposalRequest
    ) -> ResumeVersion:
        resume = self._get_owned_resume(session, candidate_id, resume_id)
        source_version = self._source_version(resume, request.source_version_id)
        next_number = max((version.version_number for version in resume.versions), default=0) + 1
        proposal = ResumeVersion(
            resume_id=resume.id,
            source_version_id=source_version.id,
            version_number=next_number,
            status=ResumeVersionStatus.PROPOSED,
            tex_content=request.tex_content,
        )
        session.add(proposal)
        session.commit()
        session.refresh(proposal)
        return proposal

    @staticmethod
    def _source_version(resume: Resume, source_version_id: int | None) -> ResumeVersion:
        approved_versions = [
            version for version in resume.versions if version.status == ResumeVersionStatus.APPROVED
        ]
        if source_version_id is None:
            if not approved_versions:
                raise ValueError("A proposal requires an approved source resume version")
            return max(approved_versions, key=lambda version: version.version_number)
        source_version = next(
            (version for version in resume.versions if version.id == source_version_id), None
        )
        if source_version is None:
            raise LookupError(f"Resume version {source_version_id} was not found")
        if source_version.status != ResumeVersionStatus.APPROVED:
            raise ValueError("A proposal source must be an approved resume version")
        return source_version

    def transition_version(
        self,
        session: Session,
        candidate_id: int,
        resume_id: int,
        version_id: int,
        status: ResumeVersionStatus,
    ) -> ResumeVersion:
        if status not in {ResumeVersionStatus.APPROVED, ResumeVersionStatus.REJECTED}:
            raise ValueError("Resume versions may only transition to APPROVED or REJECTED")
        resume = self._get_owned_resume(session, candidate_id, resume_id)
        version = session.get(ResumeVersion, version_id)
        if version is None or version.resume_id != resume.id:
            raise LookupError(f"Resume version {version_id} was not found")
        if version.status != ResumeVersionStatus.PROPOSED:
            raise ValueError("Only proposed resume versions can be approved or rejected")
        version.status = status
        session.commit()
        session.refresh(version)
        return version

    def get_resume(self, session: Session, candidate_id: int, resume_id: int) -> Resume:
        return self._get_owned_resume(session, candidate_id, resume_id)

    def list_resumes(self, session: Session, candidate_id: int) -> list[Resume]:
        if session.get(Candidate, candidate_id) is None:
            raise LookupError(f"Candidate {candidate_id} was not found")
        return list(
            session.scalars(
                select(Resume)
                .where(Resume.candidate_id == candidate_id)
                .options(selectinload(Resume.versions))
                .order_by(Resume.id)
            ).all()
        )

    def _get_owned_resume(self, session: Session, candidate_id: int, resume_id: int) -> Resume:
        resume = session.scalar(
            select(Resume)
            .where(Resume.id == resume_id, Resume.candidate_id == candidate_id)
            .options(selectinload(Resume.versions))
        )
        if resume is None:
            raise LookupError(f"Resume {resume_id} was not found")
        return resume
