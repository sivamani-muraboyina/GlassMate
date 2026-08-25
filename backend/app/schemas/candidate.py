from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SkillInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    proficiency: str | None = Field(default=None, max_length=50)


class ExperienceInput(BaseModel):
    employer: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class EducationInput(BaseModel):
    institution: str = Field(min_length=1, max_length=200)
    degree: str | None = Field(default=None, max_length=200)
    field_of_study: str | None = Field(default=None, max_length=200)


class CandidateOnboardingRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: str | None = Field(default=None, max_length=320)
    skills: list[SkillInput] = Field(default_factory=list)
    experiences: list[ExperienceInput] = Field(default_factory=list)
    education: list[EducationInput] = Field(default_factory=list)
    preferences: dict[str, object] = Field(default_factory=dict)


class SkillResponse(SkillInput):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ExperienceResponse(ExperienceInput):
    model_config = ConfigDict(from_attributes=True)

    id: int


class EducationResponse(EducationInput):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str | None
    skills: list[SkillResponse]
    experiences: list[ExperienceResponse]
    education: list[EducationResponse]
    preferences: dict[str, object]
