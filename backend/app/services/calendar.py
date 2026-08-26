from datetime import datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Application, FollowUp
from app.schemas.calendar import CalendarEvent


class CalendarClient(Protocol):
    def find_event(self, title: str, starts_at: datetime) -> CalendarEvent | None: ...

    def create_event(self, title: str, starts_at: datetime) -> CalendarEvent: ...


class CalendarService:
    def __init__(self, client: CalendarClient) -> None:
        self._client = client

    def create_follow_up(
        self,
        session: Session,
        application_id: int,
        due_at: datetime,
        title: str,
    ) -> FollowUp:
        if not title.strip():
            raise ValueError("Calendar event title must not be empty")
        application = session.get(Application, application_id)
        if application is None:
            raise LookupError(f"Application {application_id} was not found")

        existing = session.scalar(
            select(FollowUp).where(
                FollowUp.application_id == application_id,
                FollowUp.due_at == due_at,
            )
        )
        if existing is not None:
            return existing

        event = self._client.find_event(title, due_at)
        if event is None:
            event = self._client.create_event(title, due_at)
        follow_up = FollowUp(
            application_id=application_id,
            due_at=due_at,
            external_event_id=event.event_id,
        )
        session.add(follow_up)
        session.commit()
        session.refresh(follow_up)
        return follow_up