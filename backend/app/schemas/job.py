from pydantic import BaseModel, Field


class JobIngestionRequest(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=300)
    company_name: str = Field(min_length=1, max_length=300)
    location: str | None = Field(default=None, max_length=300)
    url: str = Field(min_length=1, max_length=1000)
    raw_description: str = Field(min_length=1)
    salary: str | None = Field(default=None, max_length=200)
    applicant_count: int | None = Field(default=None, ge=0)
    fingerprint: str | None = Field(default=None, max_length=128)


class JobResponse(BaseModel):
    id: int
    company_id: int | None
    title: str
    location: str | None
    source: str
    url: str
    fingerprint: str
    raw_description: str
    salary: str | None
    applicant_count: int | None
    ingested: bool = True
