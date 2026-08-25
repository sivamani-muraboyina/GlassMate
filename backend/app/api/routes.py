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
from app.schemas.resume import (
    ResumeCreateRequest,
    ResumeProposalRequest,
    ResumeResponse,
    ResumeVersionResponse,
)
from app.services.candidate_onboarding import CandidateOnboardingService
from app.services.github import GitHubRepositoryError
from app.services.project_intelligence import ProjectIntelligenceService
from app.services.resume_management import ResumeManagementService

router = APIRouter()
candidate_service = CandidateOnboardingService()
project_service = ProjectIntelligenceService()
resume_service = ResumeManagementService()


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


def resume_response(resume: object) -> ResumeResponse:
    return ResumeResponse.model_validate(resume, from_attributes=True)


@router.post("/candidates/{candidate_id}/resumes", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def create_resume(
    candidate_id: int,
    request: ResumeCreateRequest,
    session: Session = Depends(get_db),
) -> ResumeResponse:
    try:
        resume = resume_service.create_approved_resume(session, candidate_id, request)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return resume_response(resume)


@router.get("/candidates/{candidate_id}/resumes", response_model=list[ResumeResponse])
def list_resumes(candidate_id: int, session: Session = Depends(get_db)) -> list[ResumeResponse]:
    try:
        resumes = resume_service.list_resumes(session, candidate_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return [resume_response(resume) for resume in resumes]


@router.get("/candidates/{candidate_id}/resumes/{resume_id}", response_model=ResumeResponse)
def get_resume(
    candidate_id: int, resume_id: int, session: Session = Depends(get_db)
) -> ResumeResponse:
    try:
        resume = resume_service.get_resume(session, candidate_id, resume_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return resume_response(resume)


@router.post(
    "/candidates/{candidate_id}/resumes/{resume_id}/versions",
    response_model=ResumeVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resume_proposal(
    candidate_id: int,
    resume_id: int,
    request: ResumeProposalRequest,
    session: Session = Depends(get_db),
) -> ResumeVersionResponse:
    try:
        version = resume_service.create_proposal(session, candidate_id, resume_id, request)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return ResumeVersionResponse.model_validate(version, from_attributes=True)


def transition_resume_version(
    candidate_id: int,
    resume_id: int,
    version_id: int,
    target_status: str,
    session: Session,
) -> ResumeVersionResponse:
    from app.models import ResumeVersionStatus

    try:
        status_value = ResumeVersionStatus(target_status)
        version = resume_service.transition_version(
            session, candidate_id, resume_id, version_id, status_value
        )
    except (LookupError, ValueError) as error:
        status_code = status.HTTP_404_NOT_FOUND if isinstance(error, LookupError) else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=str(error)) from error
    return ResumeVersionResponse.model_validate(version, from_attributes=True)


@router.post(
    "/candidates/{candidate_id}/resumes/{resume_id}/versions/{version_id}/approve",
    response_model=ResumeVersionResponse,
)
def approve_resume_version(
    candidate_id: int,
    resume_id: int,
    version_id: int,
    session: Session = Depends(get_db),
) -> ResumeVersionResponse:
    return transition_resume_version(
        candidate_id, resume_id, version_id, "APPROVED", session
    )


@router.post(
    "/candidates/{candidate_id}/resumes/{resume_id}/versions/{version_id}/reject",
    response_model=ResumeVersionResponse,
)
def reject_resume_version(
    candidate_id: int,
    resume_id: int,
    version_id: int,
    session: Session = Depends(get_db),
) -> ResumeVersionResponse:
    return transition_resume_version(
        candidate_id, resume_id, version_id, "REJECTED", session
    )
