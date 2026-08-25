from pydantic import BaseModel, ConfigDict, Field


class ProjectImportRequest(BaseModel):
    repository_url: str = Field(min_length=1, max_length=1000)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    name: str
    purpose: str | None
    technologies: list[str]
    architecture_summary: str | None
    candidate_contribution: str | None
    repository_url: str
    content_hash: str | None
    refreshed: bool = True
