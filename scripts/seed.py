"""Seed the database with clearly-labeled SAMPLE applications.

The companies below are fictional placeholders (e.g. "Example Corp") so the
UI isn't empty on first run. They are not real job applications.

Usage:
    python scripts/seed.py           # insert sample rows (skips if data exists)
    python scripts/seed.py --force   # wipe existing rows and re-seed
"""

import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Application  # noqa: E402

TODAY = date.today()

SAMPLE_APPLICATIONS = [
    dict(
        company="Example Corp",
        role_title="Software Engineer",
        location="Austin, TX",
        work_mode="remote",
        salary_min=95000,
        salary_max=125000,
        status="interview",
        date_applied=TODAY - timedelta(days=12),
        follow_up_date=TODAY + timedelta(days=2),
        job_url="https://example.com/jobs/software-engineer",
        notes="Sample row. Technical interview scheduled with the hiring team.",
    ),
    dict(
        company="Acme Widgets Inc",
        role_title="Backend Developer (Python)",
        location="Remote - US",
        work_mode="remote",
        salary_min=105000,
        salary_max=140000,
        status="screening",
        date_applied=TODAY - timedelta(days=6),
        follow_up_date=TODAY + timedelta(days=4),
        job_url="https://example.com/jobs/backend-developer",
        notes="Sample row. Recruiter screen done, waiting on hiring-manager review.",
    ),
    dict(
        company="DemoTech Labs",
        role_title="Full-Stack Developer",
        location="Denver, CO",
        work_mode="hybrid",
        salary_min=90000,
        salary_max=115000,
        status="applied",
        date_applied=TODAY - timedelta(days=2),
        follow_up_date=TODAY + timedelta(days=12),
        job_url="https://example.com/jobs/full-stack-developer",
        notes="Sample row. Applied via company careers page.",
    ),
    dict(
        company="SampleSoft",
        role_title="Junior Software Engineer",
        location="Remote - US",
        work_mode="remote",
        salary_min=None,
        salary_max=None,
        status="wishlist",
        date_applied=None,
        follow_up_date=None,
        job_url="https://example.com/jobs/junior-engineer",
        notes="Sample row. Saved to apply after updating portfolio.",
    ),
    dict(
        company="Placeholder Systems",
        role_title="Software Engineer, Platform",
        location="Seattle, WA",
        work_mode="on-site",
        salary_min=120000,
        salary_max=155000,
        status="offer",
        date_applied=TODAY - timedelta(days=34),
        follow_up_date=TODAY + timedelta(days=1),
        job_url="https://example.com/jobs/platform-engineer",
        notes="Sample row. Offer received, reviewing details.",
    ),
    dict(
        company="Testify LLC",
        role_title="Frontend Developer",
        location="Remote - US",
        work_mode="remote",
        salary_min=85000,
        salary_max=110000,
        status="rejected",
        date_applied=TODAY - timedelta(days=28),
        follow_up_date=None,
        job_url="https://example.com/jobs/frontend-developer",
        notes="Sample row. Rejected after final round.",
    ),
    dict(
        company="MockData Analytics",
        role_title="Software Developer",
        location="Chicago, IL",
        work_mode="hybrid",
        salary_min=98000,
        salary_max=128000,
        status="applied",
        date_applied=TODAY - timedelta(days=4),
        follow_up_date=TODAY + timedelta(days=9),
        job_url=None,
        notes="Sample row. Referred by a friend.",
    ),
    dict(
        company="Fictional Foods Group",
        role_title="Software Engineer (Internal Tools)",
        location="Remote - US",
        work_mode="remote",
        salary_min=92000,
        salary_max=118000,
        status="withdrawn",
        date_applied=TODAY - timedelta(days=45),
        follow_up_date=None,
        job_url="https://example.com/jobs/internal-tools",
        notes="Sample row. Withdrew after accepting another process.",
    ),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    force = "--force" in sys.argv
    db = SessionLocal()
    try:
        existing = db.query(Application).count()
        if existing and not force:
            print(f"Database already has {existing} application(s); skipping (use --force to reseed).")
            return
        if force:
            db.query(Application).delete()
        db.add_all(Application(**row) for row in SAMPLE_APPLICATIONS)
        db.commit()
        print(f"Seeded {len(SAMPLE_APPLICATIONS)} sample applications.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
