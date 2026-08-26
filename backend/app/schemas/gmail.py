from datetime import datetime

from pydantic import BaseModel, Field


class GmailMessage(BaseModel):
    message_id: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)
    subject: str | None = None
    sender: str | None = None
    received_at: datetime | None = None
    body: str = ""


class GmailThread(BaseModel):
    thread_id: str = Field(min_length=1)
    messages: list[GmailMessage] = Field(default_factory=list)


class GmailDraft(BaseModel):
    draft_id: str = Field(min_length=1)
    thread_id: str | None = None
    recipient: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    body: str