from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import CompanyEvidence, Evidence, Job
from app.schemas.company import CompanyIntelligenceRequest


class CompanyIntelligenceService:
    def update_for_job(
        self,
        session: Session,
        job_id: int,
        request: CompanyIntelligenceRequest,
    ) -> Job:
        job = session.scalar(select(Job).where(Job.id == job_id).options(selectinload(Job.company)))
        if job is None:
            raise LookupError(f"Job {job_id} was not found")
        if job.company is None:
            raise LookupError(f"Job {job_id} has no company")

        company = job.company
        company.summary = request.summary
        company.information = request.information
        company.information_status = request.information_status
        job.role_summary = request.role_summary
        if request.evidence_content:
            evidence = Evidence(
                source_type="company_intelligence",
                source_uri=request.source_uri,
                content=request.evidence_content,
                status=request.information_status,
            )
            session.add(evidence)
            session.flush()
            session.add(CompanyEvidence(company_id=company.id, evidence_id=evidence.id))
        session.commit()
        session.refresh(job)
        return job
