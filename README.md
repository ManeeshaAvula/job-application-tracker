# Job Application Tracker

A full-stack web app for tracking job applications through a hiring pipeline — from wishlist to offer — built with a **FastAPI** backend and a **React** frontend.

## Features

- Full CRUD for job applications: company, role title, location, work mode (remote / hybrid / on-site), optional salary range, pipeline status, dates, job-posting URL, and notes
- Status pipeline: `wishlist → applied → screening → interview → offer`, plus `rejected` and `withdrawn`
- Filtering by status, work mode, and a case-insensitive company search; sorting by date applied, created date, or company
- Stats endpoint and dashboard: total count, counts per status and per work mode, and how many follow-ups come due in the next 7 days
- Input validation with Pydantic (invalid statuses, blank fields, reversed salary ranges, and malformed URLs return `422`); missing records return `404`
- Interactive API docs via FastAPI's built-in OpenAPI UI

## Tech stack

| Layer    | Technology |
|----------|------------|
| Backend  | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 |
| Database | SQLite by default; PostgreSQL via `DATABASE_URL` |
| Frontend | React 18, Vite 5 |
| Tests    | pytest + FastAPI TestClient |
| Packaging| Docker + docker-compose (API + PostgreSQL) |

## Architecture

```
frontend/ (Vite + React)  --HTTP/JSON-->  app/ (FastAPI)
                                              |
                                     app/models.py (SQLAlchemy)
                                              |
                              SQLite (default) or PostgreSQL
```

| Path | Purpose |
|------|---------|
| `app/main.py` | FastAPI application and all endpoints |
| `app/models.py` | SQLAlchemy `Application` model + status/work-mode enums |
| `app/schemas.py` | Pydantic request/response schemas and validation |
| `app/database.py` | Engine/session setup driven by `DATABASE_URL` |
| `scripts/seed.py` | Loads sample data (see "Sample data" below) |
| `tests/` | pytest suite for the API |
| `frontend/` | Vite + React UI (`src/api.js` is the API client) |

## Setup

### Backend

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/seed.py           # optional: load sample applications
uvicorn app.main:app --reload    # http://localhost:8000  (docs at /docs)
```

### Frontend

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

In development, Vite proxies `/applications`, `/stats`, and `/health` to the backend on port 8000 (see `frontend/vite.config.js`). For a production build (`npm run build`), serve the API from the same origin or set `VITE_API_BASE` to the API's base URL before building.

### Docker

```bash
docker compose up --build        # API on :8000 backed by PostgreSQL
```

## API reference

### `GET /health`
```json
{ "status": "ok" }
```

### `POST /applications` — create (returns `201`)
```json
{
  "company": "Example Corp",
  "role_title": "Software Engineer",
  "location": "Austin, TX",
  "work_mode": "remote",
  "salary_min": 95000,
  "salary_max": 125000,
  "status": "applied",
  "date_applied": "2026-10-10",
  "follow_up_date": "2026-10-24",
  "job_url": "https://example.com/jobs/software-engineer",
  "notes": "Applied via company careers page."
}
```
Only `company`, `role_title`, and `location` are required. `work_mode` defaults to `remote` and `status` to `wishlist`; salary bounds, dates, URL, and notes are optional.

### `GET /applications` — list
Query parameters:

| Param | Meaning |
|-------|---------|
| `status` | Exact status filter (e.g. `interview`) |
| `company` | Case-insensitive substring search |
| `work_mode` | `remote`, `hybrid`, or `on-site` |
| `sort_by` | `date_applied` (default), `created_at`, or `company` |
| `order` | `asc` or `desc` (default `desc`) |
| `limit` / `offset` | Pagination (default limit 100) |

### `GET /applications/{id}` — fetch one (`404` if missing)
### `PATCH /applications/{id}` — partial update (only sent fields change)
### `DELETE /applications/{id}` — delete (returns `204`)

### `GET /stats`
```json
{
  "total": 8,
  "counts_by_status": { "wishlist": 1, "applied": 2, "screening": 1, "interview": 1, "offer": 1, "rejected": 1, "withdrawn": 1 },
  "counts_by_work_mode": { "remote": 5, "hybrid": 2, "on-site": 1 },
  "follow_ups_due_next_7_days": 3
}
```
"Follow-ups due" counts applications whose `follow_up_date` falls within the next 7 days (today included) and whose status is not `rejected` or `withdrawn`.

## Configuration

| Environment variable | Default | Purpose |
|----------------------|---------|---------|
| `DATABASE_URL` | `sqlite:///./job_tracker.db` | SQLAlchemy database URL, e.g. `postgresql+psycopg2://user:pass@host:5432/dbname` |
| `VITE_API_BASE` (frontend) | *(empty = same origin)* | API base URL baked into the production frontend build |

## Running the tests

```bash
pytest
```

The suite (15 tests) covers CRUD, list filters and sorting, the stats endpoint, and validation errors (`422`/`404`). Tests run against a temporary SQLite database, so they never touch your real data.

## Sample data

`python scripts/seed.py` inserts 8 **sample applications with fictional placeholder companies** (Example Corp, Acme Widgets Inc, DemoTech Labs, …) purely so the UI isn't empty on first run. They are illustrative only — not real applications. Run with `--force` to wipe existing rows and re-seed.
