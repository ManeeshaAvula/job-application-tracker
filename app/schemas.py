"""Pydantic schemas for request/response validation."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

from .models import ApplicationStatus, WorkMode


class ApplicationBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=200)
    role_title: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=200)
    work_mode: WorkMode = WorkMode.REMOTE
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)
    status: ApplicationStatus = ApplicationStatus.WISHLIST
    date_applied: Optional[date] = None
    follow_up_date: Optional[date] = None
    job_url: Optional[HttpUrl] = None
    notes: Optional[str] = None

    @field_validator("company", "role_title", "location")
    @classmethod
    def strip_and_require_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @model_validator(mode="after")
    def salary_range_makes_sense(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_max < self.salary_min
        ):
            raise ValueError("salary_max must be greater than or equal to salary_min")
        return self


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    """Partial update — every field is optional."""

    company: Optional[str] = Field(default=None, min_length=1, max_length=200)
    role_title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    location: Optional[str] = Field(default=None, min_length=1, max_length=200)
    work_mode: Optional[WorkMode] = None
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)
    status: Optional[ApplicationStatus] = None
    date_applied: Optional[date] = None
    follow_up_date: Optional[date] = None
    job_url: Optional[HttpUrl] = None
    notes: Optional[str] = None


class ApplicationOut(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_url: Optional[str] = None  # stored/returned as a plain string
    created_at: datetime
    updated_at: datetime


class StatsOut(BaseModel):
    total: int
    counts_by_status: dict[str, int]
    counts_by_work_mode: dict[str, int]
    follow_ups_due_next_7_days: int
