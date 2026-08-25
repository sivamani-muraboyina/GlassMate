from sqlalchemy.orm import Session, joinedload

from app.models import Candidate, CandidateSkill, Education, Experience, UserPreference
from app.schemas.candidate import CandidateOnboardingRequest


class CandidateOnboardingService:
    def create_candidate(self, session: Session, request: CandidateOnboardingRequest) -> Candidate:
        candidate = Candidate(full_name=request.full_name, email=request.email)
        candidate.skills = [
            CandidateSkill(name=skill.name, proficiency=skill.proficiency)
            for skill in request.skills
        ]
        candidate.experiences = [
            Experience(
                employer=experience.employer,
                title=experience.title,
                description=experience.description,
                start_date=experience.start_date,
                end_date=experience.end_date,
            )
            for experience in request.experiences
        ]
        candidate.education = [
            Education(
                institution=education.institution,
                degree=education.degree,
                field_of_study=education.field_of_study,
            )
            for education in request.education
        ]
        candidate.preferences = UserPreference(preferences=request.preferences)

        session.add(candidate)
        session.commit()
        return self.get_candidate(session, candidate.id)

    def get_candidate(self, session: Session, candidate_id: int) -> Candidate:
        candidate = (
            session.query(Candidate)
            .options(
                joinedload(Candidate.skills),
                joinedload(Candidate.experiences),
                joinedload(Candidate.education),
                joinedload(Candidate.preferences),
            )
            .filter(Candidate.id == candidate_id)
            .one_or_none()
        )
        if candidate is None:
            raise LookupError(f"Candidate {candidate_id} was not found")
        return candidate
