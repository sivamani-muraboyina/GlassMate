from datetime import datetime

from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    event_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    starts_at: datetime