from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Application, ApplicationMode, ApplicationStatus


class ApplicationExecutionClient(Protocol):
    def supports(self, source: str) -> bool: ...

    def submit(self, application: Application) -> str: ...


@dataclass(frozen=True)
class ApplicationExecutionResult:
    application_id: int
    status: ApplicationStatus
    handoff_required: bool = False
    external_reference: str | None = None


class ApplicationExecutionService:
    def __init__(self, client: ApplicationExecutionClient) -> None:
        self._client = client

    def execute(
        self,
        session: Session,
        candidate_id: int,
        application_id: int,
        approval_granted: bool = False,
    ) -> ApplicationExecutionResult:
        application = session.scalar(
            select(Application)
            .where(Application.id == application_id, Application.candidate_id == candidate_id)
            .options(selectinload(Application.materials))
        )
        if application is None:
            raise LookupError(f"Application {application_id} was not found")
        if application.status == ApplicationStatus.APPLIED:
            return ApplicationExecutionResult(application.id, application.status)
        if application.status != ApplicationStatus.READY:
            raise ValueError("Only READY applications can be executed")
        if application.mode == ApplicationMode.PREPARE:
            return ApplicationExecutionResult(application.id, application.status, handoff_required=True)
        if application.mode == ApplicationMode.APPROVAL_REQUIRED and not approval_granted:
            raise PermissionError("Explicit approval is required before application submission")
        if not self._client.supports(application.source):
            return ApplicationExecutionResult(application.id, application.status, handoff_required=True)

        external_reference = self._client.submit(application)
        application.status = ApplicationStatus.APPLIED
        application.applied_at = datetime.now(timezone.utc)
        session.commit()
        return ApplicationExecutionResult(
            application.id,
            application.status,
            external_reference=external_reference,
        )