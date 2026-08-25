from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import RequirementKind


class JobRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    kind: RequirementKind


class JobAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    location: str | None
    salary: str | None
    applicant_count: int | None
    experience_level: str | None
    posting_time: datetime | None
    application_method: str | None
    requirements: list[JobRequirementResponse]
