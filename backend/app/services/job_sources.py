from collections.abc import Iterable
from typing import Protocol

from app.schemas.job import JobIngestionRequest


class JobSourceAdapter(Protocol):
    name: str

    def fetch(self) -> Iterable[JobIngestionRequest]:
        """Return normalized listings from a permitted job source."""
