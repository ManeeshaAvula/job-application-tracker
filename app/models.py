"""SQLAlchemy model for a tracked job application."""

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, Integer, String, Text

from .database import Base


class ApplicationStatus(str, enum.Enum):
    WISHLIST = "wishlist"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class WorkMode(str, enum.Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on-site"


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(200), nullable=False, index=True)
    role_title = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    work_mode = Column(String(20), nullable=False, default=WorkMode.REMOTE.value)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default=ApplicationStatus.WISHLIST.value, index=True)
    date_applied = Column(Date, nullable=True)
    follow_up_date = Column(Date, nullable=True)
    job_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
