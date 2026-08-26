import re

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Candidate,
    Job,
    JobMatch,
    JobRequirementMatch,
    RequirementKind,
    RequirementMatchStatus,
    Resume,
    ResumeVersion,
    ResumeVersionStatus,
)
from app.schemas.resume_strategy import ResumeStrategyResponse


class ResumeStrategyService:
    _STATUS_VALUES = {
        RequirementMatchStatus.SUPPORTED: 1.0,
        RequirementMatchStatus.PARTIALLY_SUPPORTED: 0.5,
        RequirementMatchStatus.NOT_SUPPORTED: 0.0,
    }
    _STOP_WORDS = {
        "and", "for", "the", "with", "from", "this", "that", "will", "have",
        "you", "your", "years", "work", "using", "role",
    }

    def select_resume(
        self, session: Session, job_id: int, candidate_id: int
    ) -> ResumeStrategyResponse:
        candidate = session.scalar(
            select(Candidate)
            .where(Candidate.id == candidate_id)
            .options(
                selectinload(Candidate.skills),
                selectinload(Candidate.experiences),
                selectinload(Candidate.projects),
                selectinload(Candidate.resumes).selectinload(Resume.versions),
            )
        )
        if candidate is None:
            raise LookupError(f"Candidate {candidate_id} was not found")

        job = session.scalar(
            select(Job).where(Job.id == job_id).options(selectinload(Job.requirements))
        )
        if job is None:
            raise LookupError(f"Job {job_id} was not found")

        job_match = session.scalar(
            select(JobMatch).where(JobMatch.job_id == job_id, JobMatch.candidate_id == candidate_id)
        )
        requirement_matches = {
            match.job_requirement_id: match.status
            for match in session.scalars(
                select(JobRequirementMatch).where(
                    JobRequirementMatch.candidate_id == candidate_id,
                    JobRequirementMatch.job_requirement_id.in_([item.id for item in job.requirements]),
                )
            ).all()
        }

        job_terms = self._tokens(
            " ".join([job.title, *(requirement.text for requirement in job.requirements)])
        )
        candidates = [
            (resume, version)
            for resume in candidate.resumes
            for version in resume.versions
            if version.status == ResumeVersionStatus.APPROVED
        ]
        ranked = sorted(
            [
                (
                    self._score_resume(
                        resume, version, job, job_terms, requirement_matches, candidate
                    ),
                    resume,
                    version,
                )
                for resume, version in candidates
            ],
            key=lambda item: (item[0], item[1].id, item[2].version_number),
        )
        selected = ranked[-1] if ranked else None
        selected_resume = selected[1] if selected else None
        selected_version = selected[2] if selected else None
        selection_score = selected[0] if selected else None

        strengths, missing, relevant_projects = self._explanation(
            selected_resume, selected_version, job, job_terms, requirement_matches, candidate
        )
        match_score = job_match.score if job_match is not None else None
        match_category = job_match.category if job_match is not None and job_match.category else "UNKNOWN"
        near_match = match_category == "NEAR_MATCH"
        sufficiently_aligned = selection_score is not None and selection_score >= 0.60
        recommendation = "Use the selected approved resume." if selected else "No approved resume is available for this job."
        possible_direction = None
        if near_match and not sufficiently_aligned:
            recommendation = (
                "Consider creating another resume direction using only the candidate evidence already stored."
            )
            possible_direction = self._possible_direction(job.title, strengths, relevant_projects)
        elif near_match:
            recommendation = "Use the selected approved resume; no new resume direction is required."

        return ResumeStrategyResponse(
            job_id=job_id,
            candidate_id=candidate_id,
            match_score=match_score,
            match_category=match_category,
            selected_resume_id=selected_resume.id if selected_resume else None,
            selected_version_id=selected_version.id if selected_version else None,
            selected_resume_name=selected_resume.name if selected_resume else None,
            selected_version_number=selected_version.version_number if selected_version else None,
            selection_score=selection_score,
            recommendation=recommendation,
            strengths=strengths,
            missing_requirements=missing,
            relevant_projects=relevant_projects,
            possible_direction=possible_direction,
        )

    def _score_resume(
        self,
        resume: Resume,
        version: ResumeVersion,
        job: Job,
        job_terms: set[str],
        requirement_matches: dict[int, RequirementMatchStatus],
        candidate: Candidate,
    ) -> float:
        corpus = self._tokens(f"{resume.name} {version.tex_content}")
        scoreable = [
            requirement
            for requirement in job.requirements
            if requirement.kind in {RequirementKind.REQUIRED, RequirementKind.PREFERRED}
            and requirement_matches.get(requirement.id) not in {None, RequirementMatchStatus.UNKNOWN}
        ]
        if scoreable:
            requirement_score = sum(
                self._STATUS_VALUES[requirement_matches[requirement.id]]
                * self._overlap(corpus, self._tokens(requirement.text))
                * (2 if requirement.kind == RequirementKind.REQUIRED else 1)
                for requirement in scoreable
            ) / sum(2 if requirement.kind == RequirementKind.REQUIRED else 1 for requirement in scoreable)
        else:
            requirement_score = 0.0

        evidence_scores = []
        for skill in candidate.skills:
            skill_terms = self._tokens(skill.name)
            if skill_terms & job_terms:
                evidence_scores.append(self._overlap(corpus, skill_terms))
        for project in candidate.projects:
            project_terms = self._tokens(
                f"{project.name} {project.purpose or ''} {' '.join(project.technologies)}"
            )
            if project_terms & job_terms:
                evidence_scores.append(self._overlap(corpus, project_terms))
        for experience in candidate.experiences:
            experience_terms = self._tokens(
                f"{experience.title} {experience.employer} {experience.description or ''}"
            )
            if experience_terms & job_terms:
                evidence_scores.append(self._overlap(corpus, experience_terms))
        evidence_score = sum(evidence_scores) / len(evidence_scores) if evidence_scores else 0.0
        specialization_score = self._overlap(self._tokens(resume.name), job_terms)
        return round(requirement_score * 0.7 + evidence_score * 0.2 + specialization_score * 0.1, 4)

    def _explanation(
        self,
        resume: Resume | None,
        version: ResumeVersion | None,
        job: Job,
        job_terms: set[str],
        requirement_matches: dict[int, RequirementMatchStatus],
        candidate: Candidate,
    ) -> tuple[list[str], list[str], list[str]]:
        if resume is None or version is None:
            return [], [requirement.text for requirement in job.requirements if requirement.kind == RequirementKind.REQUIRED], []
        corpus = self._tokens(f"{resume.name} {version.tex_content}")
        strengths = [
            requirement.text
            for requirement in job.requirements
            if requirement.kind in {RequirementKind.REQUIRED, RequirementKind.PREFERRED}
            and requirement_matches.get(requirement.id) in self._STATUS_VALUES
            and self._overlap(corpus, self._tokens(requirement.text)) > 0
        ]
        missing = [
            requirement.text
            for requirement in job.requirements
            if requirement.kind == RequirementKind.REQUIRED
            and (
                requirement_matches.get(requirement.id)
                in {RequirementMatchStatus.NOT_SUPPORTED, RequirementMatchStatus.UNKNOWN, None}
                or self._overlap(corpus, self._tokens(requirement.text)) == 0
            )
        ]
        relevant_projects = [
            project.name
            for project in candidate.projects
            if self._tokens(project.name) & job_terms
            and self._tokens(project.name) & corpus
        ]
        return strengths, missing, relevant_projects

    @staticmethod
    def _possible_direction(title: str, strengths: list[str], projects: list[str]) -> str:
        evidence = strengths[:2] + projects[:2]
        suffix = f" Highlight existing evidence such as {', '.join(evidence)}." if evidence else "."
        return f"Emphasize the candidate's existing evidence most relevant to the {title} role" + suffix

    @classmethod
    def _tokens(cls, value: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9]+", value.lower())
            if len(token) > 2 and token not in cls._STOP_WORDS
        }

    @staticmethod
    def _overlap(left: set[str], right: set[str]) -> float:
        return len(left & right) / len(right) if right else 0.0