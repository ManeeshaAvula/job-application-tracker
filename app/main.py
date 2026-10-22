"""Job Application Tracker API.

A small REST API for tracking job applications through a pipeline:
wishlist -> applied -> screening -> interview -> offer / rejected / withdrawn.

Run with:  uvicorn app.main:app --reload
Docs at:   http://localhost:8000/docs
"""

import os
from datetime import date, timedelta
from enum import Enum
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Application Tracker", version="1.0.0")

# The React frontend runs on a different origin; allow it in development
# (Vite dev server) and in production (the deployed static site). Override
# with the ALLOWED_ORIGINS env var (comma-separated) when needed.
_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://job-application-tracker-web.onrender.com",
]
_env_origins = os.environ.get("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = (
    [origin.strip() for origin in _env_origins.split(",") if origin.strip()]
    if _env_origins.strip()
    else _default_origins
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SortField(str, Enum):
    DATE_APPLIED = "date_applied"
    CREATED_AT = "created_at"
    COMPANY = "company"


SORTABLE_COLUMNS = {
    SortField.DATE_APPLIED: models.Application.date_applied,
    SortField.CREATED_AT: models.Application.created_at,
    SortField.COMPANY: models.Application.company,
}


def _to_db_values(payload: schemas.ApplicationBase | schemas.ApplicationUpdate, *, partial: bool):
    """Dump a schema to plain values the ORM model accepts."""
    data = payload.model_dump(exclude_unset=partial)
    for field in ("status", "work_mode"):
        if data.get(field) is not None:
            data[field] = data[field].value
    if data.get("job_url") is not None:
        data["job_url"] = str(data["job_url"])
    return data


def _get_or_404(db: Session, application_id: int) -> models.Application:
    application = db.get(models.Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/applications", response_model=schemas.ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(payload: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    application = models.Application(**_to_db_values(payload, partial=False))
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@app.get("/applications", response_model=list[schemas.ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    status_filter: Optional[models.ApplicationStatus] = Query(default=None, alias="status"),
    company: Optional[str] = Query(default=None, description="Case-insensitive substring match"),
    work_mode: Optional[models.WorkMode] = None,
    sort_by: SortField = SortField.DATE_APPLIED,
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    query = db.query(models.Application)
    if status_filter is not None:
        query = query.filter(models.Application.status == status_filter.value)
    if company:
        query = query.filter(models.Application.company.ilike(f"%{company}%"))
    if work_mode is not None:
        query = query.filter(models.Application.work_mode == work_mode.value)

    column = SORTABLE_COLUMNS[sort_by]
    query = query.order_by(column.asc() if order == "asc" else column.desc())
    return query.offset(offset).limit(limit).all()


@app.get("/applications/{application_id}", response_model=schemas.ApplicationOut)
def get_application(application_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, application_id)


@app.patch("/applications/{application_id}", response_model=schemas.ApplicationOut)
def update_application(
    application_id: int, payload: schemas.ApplicationUpdate, db: Session = Depends(get_db)
):
    application = _get_or_404(db, application_id)
    updates = _to_db_values(payload, partial=True)

    # Validate the merged salary range, since a PATCH may touch only one bound.
    new_min = updates.get("salary_min", application.salary_min)
    new_max = updates.get("salary_max", application.salary_max)
    if new_min is not None and new_max is not None and new_max < new_min:
        raise HTTPException(
            status_code=422, detail="salary_max must be greater than or equal to salary_min"
        )

    for field, value in updates.items():
        setattr(application, field, value)
    db.commit()
    db.refresh(application)
    return application


@app.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db)):
    application = _get_or_404(db, application_id)
    db.delete(application)
    db.commit()
    return None


@app.get("/stats", response_model=schemas.StatsOut)
def get_stats(db: Session = Depends(get_db)):
    applications = db.query(models.Application).all()

    counts_by_status = {s.value: 0 for s in models.ApplicationStatus}
    counts_by_work_mode = {m.value: 0 for m in models.WorkMode}
    for application in applications:
        counts_by_status[application.status] = counts_by_status.get(application.status, 0) + 1
        counts_by_work_mode[application.work_mode] = (
            counts_by_work_mode.get(application.work_mode, 0) + 1
        )

    today = date.today()
    horizon = today + timedelta(days=7)
    follow_ups_due = sum(
        1
        for a in applications
        if a.follow_up_date is not None
        and today <= a.follow_up_date <= horizon
        and a.status not in (models.ApplicationStatus.REJECTED.value, models.ApplicationStatus.WITHDRAWN.value)
    )

    return schemas.StatsOut(
        total=len(applications),
        counts_by_status=counts_by_status,
        counts_by_work_mode=counts_by_work_mode,
        follow_ups_due_next_7_days=follow_ups_due,
    )
