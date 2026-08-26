from datetime import datetime, timezone

import pytest

from app.schemas.gmail import GmailDraft, GmailMessage, GmailThread
from app.services.gmail import GmailService


class FakeGmailClient:
    def search(self, query: str) -> list[GmailMessage]:
        return [GmailMessage(message_id="m1", thread_id="t1", subject=query)]

    def read_thread(self, thread_id: str) -> GmailThread:
        return GmailThread(thread_id=thread_id)

    def create_draft(
        self, recipient: str, subject: str, body: str, thread_id: str | None = None
    ) -> GmailDraft:
        return GmailDraft(
            draft_id="d1",
            thread_id=thread_id,
            recipient=recipient,
            subject=subject,
            body=body,
        )

    def send_draft(self, draft_id: str) -> GmailMessage:
        return GmailMessage(
            message_id=draft_id,
            thread_id="t1",
            received_at=datetime.now(timezone.utc),
        )


def test_gmail_service_reads_and_creates_drafts_through_client() -> None:
    service = GmailService(FakeGmailClient())

    assert service.search("from:company.example")[0].message_id == "m1"
    assert service.read_thread("t1").thread_id == "t1"
    assert service.create_draft("candidate@example.com", "Follow up", "Hello").draft_id == "d1"


def test_gmail_service_requires_explicit_send_permission() -> None:
    service = GmailService(FakeGmailClient())

    with pytest.raises(PermissionError, match="Gmail sending is disabled"):
        service.send_draft("d1")

    assert GmailService(FakeGmailClient(), send_enabled=True).send_draft("d1").message_id == "d1"


@pytest.mark.parametrize("method, value", [("search", " "), ("read_thread", "")])
def test_gmail_service_rejects_empty_lookup_inputs(method: str, value: str) -> None:
    service = GmailService(FakeGmailClient())

    with pytest.raises(ValueError):
        getattr(service, method)(value)