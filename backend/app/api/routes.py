from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models import Candidate
from app.schemas.common import HealthResponse
from app.schemas.candidate import (
    CandidateOnboardingRequest,
    CandidateResponse,
    EducationResponse,
    ExperienceResponse,
    SkillResponse,
)
from app.schemas.project import ProjectImportRequest, ProjectResponse
from app.services.candidate_onboarding import CandidateOnboardingService
from app.services.github import GitHubRepositoryError
from app.services.project_intelligence import ProjectIntelligenceService

router = APIRouter()
candidate_service = CandidateOnboardingService()
project_service = ProjectIntelligenceService()


def candidate_response(candidate: Candidate) -> CandidateResponse:
    return CandidateResponse(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        skills=[SkillResponse.model_validate(skill, from_attributes=True) for skill in candidate.skills],
        experiences=[
            ExperienceResponse.model_validate(experience, from_attributes=True)
            for experience in candidate.experiences
        ],
        education=[
            EducationResponse.model_validate(education, from_attributes=True)
            for education in candidate.education
        ],
        preferences=candidate.preferences.preferences if candidate.preferences is not None else {},
    )


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.environment,
    )


@router.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(
    request: CandidateOnboardingRequest,
    session: Session = Depends(get_db),
) -> CandidateResponse:
    return candidate_response(candidate_service.create_candidate(session, request))


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, session: Session = Depends(get_db)) -> CandidateResponse:
    try:
        candidate = candidate_service.get_candidate(session, candidate_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return candidate_response(candidate)


@router.post("/candidates/{candidate_id}/projects/import", response_model=ProjectResponse)
def import_project(
    candidate_id: int,
    request: ProjectImportRequest,
    session: Session = Depends(get_db),
) -> ProjectResponse:
    try:
        project, refreshed = project_service.import_project(
            session, candidate_id, request.repository_url
        )
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except GitHubRepositoryError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error
    return ProjectResponse.model_validate(project, from_attributes=True).model_copy(
        update={"refreshed": refreshed}
    )
