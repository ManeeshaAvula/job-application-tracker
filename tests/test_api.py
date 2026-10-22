"""API tests: CRUD, filters, sorting, stats, and validation."""

from datetime import date, timedelta

from tests.conftest import make_application

TODAY = date.today()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get(client):
    created = make_application(
        client,
        salary_min=90000,
        salary_max=120000,
        date_applied=str(TODAY - timedelta(days=3)),
        job_url="https://example.com/jobs/1",
        notes="Referred by a friend.",
    )
    assert created["id"] >= 1
    assert created["company"] == "Example Corp"
    assert created["salary_max"] == 120000
    assert created["job_url"] == "https://example.com/jobs/1"

    fetched = client.get(f"/applications/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["role_title"] == "Software Engineer"


def test_get_missing_returns_404(client):
    assert client.get("/applications/9999").status_code == 404


def test_update_partial(client):
    created = make_application(client)
    response = client.patch(
        f"/applications/{created['id']}",
        json={"status": "interview", "notes": "Moved to interviews."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "interview"
    assert body["notes"] == "Moved to interviews."
    assert body["company"] == "Example Corp"  # untouched field preserved


def test_update_missing_returns_404(client):
    assert client.patch("/applications/9999", json={"status": "offer"}).status_code == 404


def test_delete(client):
    created = make_application(client)
    assert client.delete(f"/applications/{created['id']}").status_code == 204
    assert client.get(f"/applications/{created['id']}").status_code == 404
    assert client.delete(f"/applications/{created['id']}").status_code == 404


def test_list_and_filters(client):
    make_application(client, company="Alpha LLC", status="applied", work_mode="remote")
    make_application(client, company="Alphabet Soup Co", status="interview", work_mode="hybrid")
    make_application(client, company="Beta Corp", status="applied", work_mode="on-site")

    assert len(client.get("/applications").json()) == 3

    applied = client.get("/applications", params={"status": "applied"}).json()
    assert {a["company"] for a in applied} == {"Alpha LLC", "Beta Corp"}

    # Company filter is a case-insensitive substring search.
    alpha = client.get("/applications", params={"company": "ALPHA"}).json()
    assert {a["company"] for a in alpha} == {"Alpha LLC", "Alphabet Soup Co"}

    remote = client.get("/applications", params={"work_mode": "remote"}).json()
    assert [a["company"] for a in remote] == ["Alpha LLC"]


def test_list_sorting_by_company(client):
    make_application(client, company="Zeta Inc")
    make_application(client, company="Alpha LLC")
    ordered = client.get(
        "/applications", params={"sort_by": "company", "order": "asc"}
    ).json()
    assert [a["company"] for a in ordered] == ["Alpha LLC", "Zeta Inc"]


def test_stats(client):
    make_application(client, status="applied", follow_up_date=str(TODAY + timedelta(days=3)))
    make_application(client, status="applied", follow_up_date=str(TODAY + timedelta(days=30)))
    make_application(client, status="interview")
    make_application(client, status="rejected", follow_up_date=str(TODAY + timedelta(days=2)))

    stats = client.get("/stats").json()
    assert stats["total"] == 4
    assert stats["counts_by_status"]["applied"] == 2
    assert stats["counts_by_status"]["interview"] == 1
    assert stats["counts_by_status"]["offer"] == 0
    # Only the non-terminal application due within 7 days counts.
    assert stats["follow_ups_due_next_7_days"] == 1


def test_stats_empty(client):
    stats = client.get("/stats").json()
    assert stats["total"] == 0
    assert stats["follow_ups_due_next_7_days"] == 0


def test_validation_missing_required_field(client):
    response = client.post("/applications", json={"company": "No Role Inc"})
    assert response.status_code == 422


def test_validation_blank_company(client):
    response = client.post(
        "/applications",
        json={"company": "   ", "role_title": "Engineer", "location": "Remote"},
    )
    assert response.status_code == 422


def test_validation_bad_status_and_work_mode(client):
    response = client.post(
        "/applications",
        json={
            "company": "Example Corp",
            "role_title": "Engineer",
            "location": "Remote",
            "status": "ghosted",
        },
    )
    assert response.status_code == 422

    response = client.post(
        "/applications",
        json={
            "company": "Example Corp",
            "role_title": "Engineer",
            "location": "Remote",
            "work_mode": "telepathic",
        },
    )
    assert response.status_code == 422


def test_validation_salary_range(client):
    response = client.post(
        "/applications",
        json={
            "company": "Example Corp",
            "role_title": "Engineer",
            "location": "Remote",
            "salary_min": 150000,
            "salary_max": 100000,
        },
    )
    assert response.status_code == 422


def test_validation_bad_job_url(client):
    response = client.post(
        "/applications",
        json={
            "company": "Example Corp",
            "role_title": "Engineer",
            "location": "Remote",
            "job_url": "not-a-url",
        },
    )
    assert response.status_code == 422
