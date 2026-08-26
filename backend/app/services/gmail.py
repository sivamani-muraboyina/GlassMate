from typing import Protocol

from app.schemas.gmail import GmailDraft, GmailMessage, GmailThread


class GmailClient(Protocol):
    def search(self, query: str) -> list[GmailMessage]: ...

    def read_thread(self, thread_id: str) -> GmailThread: ...

    def create_draft(
        self, recipient: str, subject: str, body: str, thread_id: str | None = None
    ) -> GmailDraft: ...

    def send_draft(self, draft_id: str) -> GmailMessage: ...


class GmailService:
    def __init__(self, client: GmailClient, send_enabled: bool = False) -> None:
        self._client = client
        self._send_enabled = send_enabled

    def search(self, query: str) -> list[GmailMessage]:
        if not query.strip():
            raise ValueError("Gmail search query must not be empty")
        return self._client.search(query)

    def read_thread(self, thread_id: str) -> GmailThread:
        if not thread_id.strip():
            raise ValueError("Gmail thread ID must not be empty")
        return self._client.read_thread(thread_id)

    def create_draft(
        self, recipient: str, subject: str, body: str, thread_id: str | None = None
    ) -> GmailDraft:
        if not recipient.strip():
            raise ValueError("Gmail draft recipient must not be empty")
        if not subject.strip():
            raise ValueError("Gmail draft subject must not be empty")
        if not body.strip():
            raise ValueError("Gmail draft body must not be empty")
        return self._client.create_draft(recipient, subject, body, thread_id)

    def send_draft(self, draft_id: str) -> GmailMessage:
        if not self._send_enabled:
            raise PermissionError("Gmail sending is disabled")
        if not draft_id.strip():
            raise ValueError("Gmail draft ID must not be empty")
        return self._client.send_draft(draft_id)