from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Candidate,
    Job,
    JobMatch,
    JobRequirement,
    JobRequirementMatch,
    RequirementKind,
    RequirementMatchStatus,
)
from app.schemas.job_match import JobMatchRequest


class JobMatchingService:
    _STATUS_VALUES = {
        RequirementMatchStatus.SUPPORTED: 1.0,
        RequirementMatchStatus.PARTIALLY_SUPPORTED: 0.5,
        RequirementMatchStatus.NOT_SUPPORTED: 0.0,
    }
    _REQUIREMENT_WEIGHTS = {
        RequirementKind.REQUIRED: 2,
        RequirementKind.PREFERRED: 1,
    }

    def calculate(
        self, session: Session, job_id: int, candidate_id: int, request: JobMatchRequest
    ) -> JobMatch:
        if session.get(Candidate, candidate_id) is None:
            raise LookupError(f"Candidate {candidate_id} was not found")
        job = session.scalar(
            select(Job).where(Job.id == job_id).options(selectinload(Job.requirements))
        )
        if job is None:
            raise LookupError(f"Job {job_id} was not found")
        requirements_by_id = {requirement.id: requirement for requirement in job.requirements}
        existing_matches = {
            match.job_requirement_id: match
            for match in session.scalars(
                select(JobRequirementMatch).where(JobRequirementMatch.candidate_id == candidate_id)
            ).all()
            if match.job_requirement_id in requirements_by_id
        }
        for item in request.requirements:
            requirement = requirements_by_id.get(item.requirement_id)
            if requirement is None:
                raise ValueError(f"Requirement {item.requirement_id} does not belong to job {job_id}")
            match = existing_matches.get(item.requirement_id)
            if match is None:
                match = JobRequirementMatch(
                    job_requirement_id=requirement.id,
                    candidate_id=candidate_id,
                    status=item.status,
                )
                session.add(match)
            else:
                match.status = item.status

        session.flush()
        score, category = self._score(job.requirements, existing_matches, request, candidate_id, session)
        job_match = session.scalar(
            select(JobMatch).where(JobMatch.job_id == job_id, JobMatch.candidate_id == candidate_id)
        )
        if job_match is None:
            job_match = JobMatch(job_id=job_id, candidate_id=candidate_id)
            session.add(job_match)
        job_match.score = score
        job_match.category = category
        session.commit()
        session.refresh(job_match)
        return job_match

    def _score(
        self,
        requirements: list[JobRequirement],
        existing_matches: dict[int, JobRequirementMatch],
        request: JobMatchRequest,
        candidate_id: int,
        session: Session,
    ) -> tuple[float | None, str]:
        submitted = {item.requirement_id: item.status for item in request.requirements}
        numerator = 0.0
        denominator = 0
        for requirement in requirements:
            weight = self._REQUIREMENT_WEIGHTS.get(requirement.kind)
            if weight is None:
                continue
            status = submitted.get(requirement.id)
            if status is None:
                persisted = existing_matches.get(requirement.id)
                status = persisted.status if persisted is not None else None
            if status is None or status == RequirementMatchStatus.UNKNOWN:
                continue
            numerator += self._STATUS_VALUES[status] * weight
            denominator += weight
        if denominator == 0:
            return None, "UNKNOWN"
        score = numerator / denominator
        if score > 0.70:
            category = "STRONG_MATCH"
        elif score >= 0.50:
            category = "NEAR_MATCH"
        else:
            category = "POOR_MATCH"
        return score, category
