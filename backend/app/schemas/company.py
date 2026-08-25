from pydantic import BaseModel, ConfigDict, Field

from app.models import EvidenceStatus


class CompanyIntelligenceRequest(BaseModel):
    summary: str | None = None
    role_summary: str | None = None
    information: dict[str, object] = Field(default_factory=dict)
    information_status: EvidenceStatus = EvidenceStatus.UNKNOWN
    source_uri: str | None = Field(default=None, max_length=1000)
    evidence_content: str | None = None


class CompanyIntelligenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: int
    company_name: str
    role: str
    role_summary: str | None
    salary: str | None
    location: str | None
    summary: str | None
    information: dict[str, object]
    information_status: EvidenceStatus
    evidence_recorded: bool
