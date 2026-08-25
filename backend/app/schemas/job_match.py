from pydantic import BaseModel, Field

from app.models import RequirementMatchStatus


class RequirementMatchInput(BaseModel):
    requirement_id: int = Field(gt=0)
    status: RequirementMatchStatus


class JobMatchRequest(BaseModel):
    requirements: list[RequirementMatchInput]


class RequirementMatchResponse(BaseModel):
    requirement_id: int
    status: RequirementMatchStatus
    kind: str
    text: str


class JobMatchResponse(BaseModel):
    job_id: int
    candidate_id: int
    score: float | None
    category: str
    requirements: list[RequirementMatchResponse]
