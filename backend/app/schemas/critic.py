from typing import Literal

from pydantic import BaseModel


class CriticFinding(BaseModel):
    issue: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    evidence: str
    correction: str


class CriticResponse(BaseModel):
    application_id: int
    candidate_id: int
    result: Literal["PASS", "FAIL"]
    findings: list[CriticFinding]
