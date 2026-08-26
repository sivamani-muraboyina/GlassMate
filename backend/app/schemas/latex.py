from typing import Literal

from pydantic import BaseModel


class LatexCompilationResponse(BaseModel):
    version_id: int
    status: Literal["SUCCESS", "FAILED", "UNAVAILABLE"]
    pdf_filename: str | None
    pdf_size_bytes: int | None
    log: str
    error: str | None