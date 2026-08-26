from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Application,
    ApplicationMaterial,
    ApplicationStatus,
    Candidate,
    Job,
    JobMatch,
    Resume,
    ResumeVersion,
    ResumeVersionStatus,
)
from app.schemas.application import ApplicationPreparationRequest


class ApplicationPreparationService:
    def prepare(
        self,
        session: Session,
        candidate_id: int,
        job_id: int,
        request: ApplicationPreparationRequest,
    ) -> Application:
        if session.get(Candidate, candidate_id) is None:
            raise LookupError(f"Candidate {candidate_id} was not found")
        job = session.scalar(select(Job).where(Job.id == job_id))
        if job is None:
            raise LookupError(f"Job {job_id} was not found")

        if request.idempotency_key is not None:
            existing = session.scalar(
                select(Application)
                .where(Application.idempotency_key == request.idempotency_key)
                .options(selectinload(Application.materials))
            )
            if existing is not None:
                if existing.candidate_id != candidate_id or existing.job_id != job_id:
                    raise ValueError("Idempotency key is already associated with another application")
                return existing

        version = session.scalar(
            select(ResumeVersion)
            .join(Resume)
            .where(
                ResumeVersion.id == request.resume_version_id,
                Resume.candidate_id == candidate_id,
            )
        )
        if version is None:
            raise LookupError(f"Resume version {request.resume_version_id} was not found")
        if version.status not in {ResumeVersionStatus.APPROVED, ResumeVersionStatus.PROPOSED}:
            raise ValueError("Only approved or proposed resume versions can be used")

        match = session.scalar(
            select(JobMatch).where(JobMatch.job_id == job_id, JobMatch.candidate_id == candidate_id)
        )
        application = Application(
            job_id=job.id,
            candidate_id=candidate_id,
            resume_version_id=version.id,
            mode=request.mode,
            status=ApplicationStatus.READY,
            idempotency_key=request.idempotency_key,
            job_url_snapshot=job.url,
            jd_snapshot=job.raw_description,
            match_score=match.score if match is not None else None,
            source=job.source,
            materials=[
                ApplicationMaterial(
                    material_type=material.material_type,
                    content=material.content,
                    claims=material.claims,
                )
                for material in request.materials
            ],
        )
        session.add(application)
        session.commit()
        return self.get_application(session, candidate_id, application.id)

    def get_application(self, session: Session, candidate_id: int, application_id: int) -> Application:
        application = session.scalar(
            select(Application)
            .where(Application.id == application_id, Application.candidate_id == candidate_id)
            .options(selectinload(Application.materials))
        )
        if application is None:
            raise LookupError(f"Application {application_id} was not found")
        return application
