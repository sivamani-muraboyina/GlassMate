from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Company, Job
from app.schemas.job import JobIngestionRequest


class JobIngestionService:
    def ingest(self, session: Session, request: JobIngestionRequest) -> tuple[Job, bool]:
        fingerprint = request.fingerprint or self._fingerprint(request)
        existing = session.scalar(
            select(Job).where(Job.source == request.source, Job.fingerprint == fingerprint)
        )
        if existing is not None:
            return existing, False

        company = session.scalar(select(Company).where(Company.name == request.company_name))
        if company is None:
            company = Company(name=request.company_name)
            session.add(company)
            session.flush()

        job = Job(
            company_id=company.id,
            title=request.title,
            location=request.location,
            source=request.source,
            url=request.url,
            fingerprint=fingerprint,
            raw_description=request.raw_description,
            salary=request.salary,
            applicant_count=request.applicant_count,
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        return job, True

    @staticmethod
    def _fingerprint(request: JobIngestionRequest) -> str:
        normalized = "|".join(
            [
                request.source.strip().lower(),
                request.url.strip().lower(),
                request.title.strip().lower(),
                request.company_name.strip().lower(),
                request.raw_description.strip(),
            ]
        )
        return sha256(normalized.encode("utf-8")).hexdigest()
