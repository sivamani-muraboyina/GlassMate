import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Company, CompanyEvidence, Evidence, EvidenceStatus, Job
from app.schemas.company import CompanyIntelligenceRequest
from app.services.company_intelligence import CompanyIntelligenceService
import app.models.entities  # noqa: F401


def test_company_intelligence_stores_status_and_source_evidence() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        company = Company(name="Example AI")
        session.add(company)
        session.flush()
        job = Job(
            company_id=company.id,
            title="ML Engineer",
            source="feed",
            url="https://jobs.example/ml",
            fingerprint="company-1",
            raw_description="description",
            salary=None,
            location="Remote",
        )
        session.add(job)
        session.commit()
        session.refresh(job)

        updated = CompanyIntelligenceService().update_for_job(
            session,
            job.id,
            CompanyIntelligenceRequest(
                summary="Builds machine learning products.",
                role_summary="Works on model-serving systems.",
                information={"location": "Remote"},
                information_status=EvidenceStatus.VERIFIED,
                source_uri="https://example.ai/about",
                evidence_content="Company about page supplied by the user.",
            ),
        )

        assert updated.company is not None
        assert updated.company.information_status == EvidenceStatus.VERIFIED
        assert updated.company.summary == "Builds machine learning products."
        assert updated.role_summary == "Works on model-serving systems."
        assert session.query(Evidence).count() == 1
        assert session.query(CompanyEvidence).count() == 1


def test_company_intelligence_requires_a_company() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        job = Job(
            title="Engineer",
            source="feed",
            url="https://jobs.example/unknown-company",
            fingerprint="company-2",
            raw_description="description",
        )
        session.add(job)
        session.commit()
        session.refresh(job)

        with pytest.raises(LookupError, match="no company"):
            CompanyIntelligenceService().update_for_job(
                session, job.id, CompanyIntelligenceRequest()
            )
