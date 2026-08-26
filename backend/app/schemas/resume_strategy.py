from pydantic import BaseModel


class ResumeStrategyResponse(BaseModel):
    job_id: int
    candidate_id: int
    match_score: float | None
    match_category: str
    selected_resume_id: int | None
    selected_version_id: int | None
    selected_resume_name: str | None
    selected_version_number: int | None
    selection_score: float | None
    recommendation: str
    strengths: list[str]
    missing_requirements: list[str]
    relevant_projects: list[str]
    possible_direction: str | None