from pydantic import BaseModel, ConfigDict, Field

from app.models import ResumeVersionStatus


class ResumeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    template_source: str | None = None
    tex_content: str = Field(min_length=1)


class ResumeProposalRequest(BaseModel):
    tex_content: str = Field(min_length=1)
    source_version_id: int | None = Field(default=None, gt=0)


class ResumeVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_version_id: int | None
    version_number: int
    status: ResumeVersionStatus
    tex_content: str


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    name: str
    template_source: str | None
    versions: list[ResumeVersionResponse]
