from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Application, ApplicationMode, ApplicationStatus
from app.services.application_execution import ApplicationExecutionService
import app.models.entities  # noqa: F401


class FakeApplicationClient:
    def __init__(self, supported: bool = True) -> None:
        self.supported = supported
        self.submissions = 0

    def supports(self, source: str) -> bool:
        return self.supported

    def submit(self, application: Application) -> str:
        self.submissions += 1
        return f"submission-{application.id}"


def setup_session(mode: ApplicationMode) -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add(
        Application(
            id=1,
            job_id=1,
            candidate_id=1,
            mode=mode,
            status=ApplicationStatus.READY,
            source="permitted-source",
        )
    )
    session.commit()
    return session


def test_prepare_mode_returns_handoff_without_submission() -> None:
    session = setup_session(ApplicationMode.PREPARE)
    client = FakeApplicationClient()

    result = ApplicationExecutionService(client).execute(session, 1, 1)

    assert result.handoff_required is True
    assert result.status == ApplicationStatus.READY
    assert client.submissions == 0


def test_approval_required_mode_needs_approval_then_marks_applied() -> None:
    session = setup_session(ApplicationMode.APPROVAL_REQUIRED)
    client = FakeApplicationClient()
    service = ApplicationExecutionService(client)

    with pytest.raises(PermissionError, match="Explicit approval"):
        service.execute(session, 1, 1)

    result = service.execute(session, 1, 1, approval_granted=True)

    assert result.status == ApplicationStatus.APPLIED
    assert result.external_reference == "submission-1"
    assert client.submissions == 1
    assert session.get(Application, 1).applied_at is not None


def test_unsupported_source_and_repeated_execution_are_safe() -> None:
    session = setup_session(ApplicationMode.AUTO_APPLY)
    client = FakeApplicationClient(supported=False)
    service = ApplicationExecutionService(client)

    result = service.execute(session, 1, 1)

    assert result.handoff_required is True
    assert result.status == ApplicationStatus.READY
    assert client.submissions == 0

    session.get(Application, 1).status = ApplicationStatus.APPLIED
    session.commit()
    result = service.execute(session, 1, 1)
    assert result.status == ApplicationStatus.APPLIED


def test_execution_validates_ownership_and_status() -> None:
    session = setup_session(ApplicationMode.AUTO_APPLY)
    service = ApplicationExecutionService(FakeApplicationClient())

    with pytest.raises(LookupError, match="Application 1 was not found"):
        service.execute(session, 2, 1)

    session.get(Application, 1).status = ApplicationStatus.DISCOVERED
    session.commit()
    with pytest.raises(ValueError, match="Only READY"):
        service.execute(session, 1, 1)