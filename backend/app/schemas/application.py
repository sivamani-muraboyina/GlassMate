from pydantic import BaseModel, Field

from app.models import ApplicationMode, ApplicationStatus


class ApplicationMaterialInput(BaseModel):
    material_type: str = Field(min_length=1, max_length=80)
    content: str = Field(min_length=1)
    claims: list[int] = Field(default_factory=list)


class ApplicationPreparationRequest(BaseModel):
    resume_version_id: int = Field(gt=0)
    mode: ApplicationMode = ApplicationMode.PREPARE
    materials: list[ApplicationMaterialInput] = Field(default_factory=list)
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=200)


class ApplicationMaterialResponse(ApplicationMaterialInput):
    id: int


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    resume_version_id: int | None
    mode: ApplicationMode
    status: ApplicationStatus
    job_url: str
    job_description: str
    match_score: float | None
    source: str
    materials: list[ApplicationMaterialResponse]
