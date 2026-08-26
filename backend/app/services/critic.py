from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Application,
    Candidate,
    Claim,
    Job,
    JobRequirement,
    JobRequirementMatch,
    RequirementKind,
    RequirementMatchStatus,
    Resume,
    ResumeVersion,
    ResumeVersionStatus,
)
from app.schemas.critic import CriticFinding, CriticResponse


class CriticService:
    def review(
        self, session: Session, candidate_id: int, application_id: int
    ) -> CriticResponse:
        application = session.scalar(
            select(Application)
            .where(Application.id == application_id, Application.candidate_id == candidate_id)
            .options(selectinload(Application.materials))
        )
        if application is None:
            raise LookupError(f"Application {application_id} was not found")

        job = session.get(Job, application.job_id)
        if job is None:
            raise LookupError(f"Job {application.job_id} was not found")
        candidate = session.get(Candidate, candidate_id)
        if candidate is None:
            raise LookupError(f"Candidate {candidate_id} was not found")
        version = session.scalar(
            select(ResumeVersion)
            .join(Resume)
            .where(ResumeVersion.id == application.resume_version_id, Resume.candidate_id == candidate_id)
        )
        findings: list[CriticFinding] = []
        if version is None:
            findings.append(
                CriticFinding(
                    issue="The application has no resume version owned by the candidate.",
                    severity="HIGH",
                    evidence=f"resume_version_id={application.resume_version_id}",
                    correction="Attach an approved or proposed resume version owned by the candidate.",
                )
            )
        elif version.status not in {ResumeVersionStatus.APPROVED, ResumeVersionStatus.PROPOSED}:
            findings.append(
                CriticFinding(
                    issue="The selected resume version is not usable.",
                    severity="HIGH",
                    evidence=f"resume_version_id={version.id}, status={version.status.value}",
                    correction="Select an approved resume or review the proposed version before use.",
                )
            )

        if not application.materials:
            findings.append(
                CriticFinding(
                    issue="The application package contains no materials.",
                    severity="MEDIUM",
                    evidence=f"application_id={application.id}, material_count=0",
                    correction="Add the materials required by the target application before submission.",
                )
            )

        claim_ids = {
            claim_id
            for material in application.materials
            for claim_id in material.claims
        }
        if claim_ids:
            claims = {
                claim.id: claim
                for claim in session.scalars(select(Claim).where(Claim.id.in_(claim_ids))).all()
            }
            for claim_id in sorted(claim_ids):
                claim = claims.get(claim_id)
                if claim is None:
                    findings.append(
                        CriticFinding(
                            issue="A material references a claim that does not exist.",
                            severity="HIGH",
                            evidence=f"claim_id={claim_id}",
                            correction="Remove the reference or attach the material to a stored candidate claim.",
                        )
                    )
                elif claim.status.value != "VERIFIED":
                    findings.append(
                        CriticFinding(
                            issue="A material references a claim that is not verified.",
                            severity="HIGH",
                            evidence=f"claim_id={claim.id}, status={claim.status.value}",
                            correction="Use verified evidence or remove the unsupported claim.",
                        )
                    )

        requirements = session.scalars(
            select(JobRequirement).where(
                JobRequirement.job_id == job.id,
                JobRequirement.kind == RequirementKind.REQUIRED,
            )
        ).all()
        matches = {
            match.job_requirement_id: match.status
            for match in session.scalars(
                select(JobRequirementMatch).where(
                    JobRequirementMatch.candidate_id == candidate_id,
                    JobRequirementMatch.job_requirement_id.in_([requirement.id for requirement in requirements]),
                )
            ).all()
        }
        for requirement in requirements:
            match_status = matches.get(requirement.id, RequirementMatchStatus.UNKNOWN)
            if match_status in {RequirementMatchStatus.NOT_SUPPORTED, RequirementMatchStatus.UNKNOWN}:
                findings.append(
                    CriticFinding(
                        issue="A required job requirement is not supported by the candidate evidence.",
                        severity="MEDIUM",
                        evidence=f"requirement={requirement.text}, status={match_status.value}",
                        correction="Address the gap honestly or do not submit this application package.",
                    )
                )

        return CriticResponse(
            application_id=application.id,
            candidate_id=candidate_id,
            result="FAIL" if findings else "PASS",
            findings=findings,
        )
