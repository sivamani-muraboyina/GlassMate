from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Application, Candidate, FollowUp
from app.schemas.calendar import CalendarEvent
from app.services.calendar import CalendarService
import app.models.entities  # noqa: F401


class FakeCalendarClient:
    def __init__(self, existing: CalendarEvent | None = None) -> None:
        self.existing = existing
        self.created = 0

    def find_event(self, title: str, starts_at: datetime) -> CalendarEvent | None:
        return self.existing

    def create_event(self, title: str, starts_at: datetime) -> CalendarEvent:
        self.created += 1
        return CalendarEvent(event_id="event-1", title=title, starts_at=starts_at)


def setup_session() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add(Application(job_id=1, candidate_id=1))
    session.commit()
    return session


def test_calendar_service_reuses_existing_follow_up() -> None:
    session = setup_session()
    due_at = datetime(2026, 9, 8, 9, tzinfo=timezone.utc)
    session.add(FollowUp(application_id=1, due_at=due_at, external_event_id="event-existing"))
    session.commit()
    client = FakeCalendarClient()

    follow_up = CalendarService(client).create_follow_up(session, 1, due_at, "Follow up")

    assert follow_up.external_event_id == "event-existing"
    assert client.created == 0


def test_calendar_service_reuses_remote_event_or_creates_one() -> None:
    due_at = datetime(2026, 9, 8, 9, tzinfo=timezone.utc)
    session = setup_session()
    existing_client = FakeCalendarClient(
        CalendarEvent(event_id="event-found", title="Follow up", starts_at=due_at)
    )

    follow_up = CalendarService(existing_client).create_follow_up(session, 1, due_at, "Follow up")

    assert follow_up.external_event_id == "event-found"
    assert existing_client.created == 0

    session = setup_session()
    new_client = FakeCalendarClient()
    follow_up = CalendarService(new_client).create_follow_up(session, 1, due_at, "Follow up")

    assert follow_up.external_event_id == "event-1"
    assert new_client.created == 1


def test_calendar_service_validates_application_and_title() -> None:
    session = setup_session()
    service = CalendarService(FakeCalendarClient())
    due_at = datetime(2026, 9, 8, 9, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="title must not be empty"):
        service.create_follow_up(session, 1, due_at, " ")
    with pytest.raises(LookupError, match="Application 2 was not found"):
        service.create_follow_up(session, 2, due_at, "Follow up")