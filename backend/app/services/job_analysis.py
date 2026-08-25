from datetime import datetime
import re

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Job, JobRequirement, RequirementKind


class JobAnalysisService:
    def analyze(self, session: Session, job_id: int) -> Job:
        job = session.scalar(
            select(Job).where(Job.id == job_id).options(selectinload(Job.requirements))
        )
        if job is None:
            raise LookupError(f"Job {job_id} was not found")

        job.experience_level = self._metadata_value(job.raw_description, "experience level")
        job.application_method = self._metadata_value(job.raw_description, "application method")
        job.posting_time = self._metadata_datetime(job.raw_description, "posting time")
        job.requirements.clear()
        job.requirements.extend(self._requirements(job.raw_description))
        session.commit()
        session.refresh(job)
        return job

    @staticmethod
    def _metadata_value(description: str, label: str) -> str | None:
        pattern = rf"^\s*{re.escape(label)}\s*:\s*(.+?)\s*$"
        for line in description.splitlines():
            match = re.match(pattern, line, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip() or None
        return None

    @classmethod
    def _metadata_datetime(cls, description: str, label: str) -> datetime | None:
        value = cls._metadata_value(description, label)
        if value is None:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _requirements(description: str) -> list[JobRequirement]:
        section_kinds = {
            "required": RequirementKind.REQUIRED,
            "requirements": RequirementKind.REQUIRED,
            "qualifications": RequirementKind.REQUIRED,
            "preferred": RequirementKind.PREFERRED,
            "preferred qualifications": RequirementKind.PREFERRED,
            "responsibilities": RequirementKind.RESPONSIBILITY,
            "responsibility": RequirementKind.RESPONSIBILITY,
            "other": RequirementKind.OTHER,
        }
        current_kind: RequirementKind | None = None
        requirements: list[JobRequirement] = []
        for raw_line in description.splitlines():
            line = raw_line.strip()
            normalized_heading = line.removeprefix("#").strip().rstrip(":").lower()
            if normalized_heading in section_kinds:
                current_kind = section_kinds[normalized_heading]
                continue
            if current_kind is None or not line:
                continue
            item = line.lstrip("-* ").strip()
            if item:
                requirements.append(JobRequirement(text=item, kind=current_kind))
        return requirements
