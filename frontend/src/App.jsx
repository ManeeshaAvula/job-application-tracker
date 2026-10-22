import { useCallback, useEffect, useState } from "react";
import {
  createApplication,
  deleteApplication,
  getStats,
  listApplications,
  updateApplication,
} from "./api";

const STATUSES = ["wishlist", "applied", "screening", "interview", "offer", "rejected", "withdrawn"];
const WORK_MODES = ["remote", "hybrid", "on-site"];

const EMPTY_FORM = {
  company: "",
  role_title: "",
  location: "",
  work_mode: "remote",
  salary_min: "",
  salary_max: "",
  status: "wishlist",
  date_applied: "",
  follow_up_date: "",
  job_url: "",
  notes: "",
};

function formatSalary(app) {
  const fmt = (n) => `$${Math.round(n / 1000)}k`;
  if (app.salary_min && app.salary_max) return `${fmt(app.salary_min)} – ${fmt(app.salary_max)}`;
  if (app.salary_min) return `${fmt(app.salary_min)}+`;
  if (app.salary_max) return `up to ${fmt(app.salary_max)}`;
  return "—";
}

export default function App() {
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [workModeFilter, setWorkModeFilter] = useState("");
  const [search, setSearch] = useState("");
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const [apps, statsData] = await Promise.all([
        listApplications({ status: statusFilter, company: search, workMode: workModeFilter }),
        getStats(),
      ]);
      setApplications(apps);
      setStats(statsData);
      setError("");
    } catch (err) {
      setError(`Could not reach the API. Is the backend running? (${err.message})`);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, workModeFilter, search]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function handleFormChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function toPayload() {
    const payload = { ...form };
    payload.salary_min = form.salary_min === "" ? null : Number(form.salary_min);
    payload.salary_max = form.salary_max === "" ? null : Number(form.salary_max);
    payload.date_applied = form.date_applied || null;
    payload.follow_up_date = form.follow_up_date || null;
    payload.job_url = form.job_url || null;
    payload.notes = form.notes || null;
    return payload;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      if (editingId) {
        await updateApplication(editingId, toPayload());
      } else {
        await createApplication(toPayload());
      }
      setForm(EMPTY_FORM);
      setEditingId(null);
      await refresh();
    } catch (err) {
      setError(`Save failed — ${err.message}`);
    }
  }

  function startEdit(app) {
    setEditingId(app.id);
    setForm({
      company: app.company,
      role_title: app.role_title,
      location: app.location,
      work_mode: app.work_mode,
      salary_min: app.salary_min ?? "",
      salary_max: app.salary_max ?? "",
      status: app.status,
      date_applied: app.date_applied ?? "",
      follow_up_date: app.follow_up_date ?? "",
      job_url: app.job_url ?? "",
      notes: app.notes ?? "",
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleDelete(app) {
    if (!window.confirm(`Delete the ${app.company} application?`)) return;
    try {
      await deleteApplication(app.id);
      if (editingId === app.id) {
        setEditingId(null);
        setForm(EMPTY_FORM);
      }
      await refresh();
    } catch (err) {
      setError(`Delete failed — ${err.message}`);
    }
  }

  return (
    <div className="page">
      <header>
        <h1>Job Application Tracker</h1>
        <p className="subtitle">Track every application from wishlist to offer.</p>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {stats && (
        <section className="stats-grid">
          <div className="stat-card total">
            <span className="stat-number">{stats.total}</span>
            <span className="stat-label">Total applications</span>
          </div>
          {STATUSES.map((s) => (
            <div key={s} className="stat-card">
              <span className="stat-number">{stats.counts_by_status[s] ?? 0}</span>
              <span className="stat-label">{s}</span>
            </div>
          ))}
          <div className="stat-card follow-ups">
            <span className="stat-number">{stats.follow_ups_due_next_7_days}</span>
            <span className="stat-label">Follow-ups due (7 days)</span>
          </div>
        </section>
      )}

      <section className="panel">
        <h2>{editingId ? "Edit application" : "Add an application"}</h2>
        <form className="app-form" onSubmit={handleSubmit}>
          <label>
            Company *
            <input name="company" value={form.company} onChange={handleFormChange} required />
          </label>
          <label>
            Role title *
            <input name="role_title" value={form.role_title} onChange={handleFormChange} required />
          </label>
          <label>
            Location *
            <input name="location" value={form.location} onChange={handleFormChange} required />
          </label>
          <label>
            Work mode
            <select name="work_mode" value={form.work_mode} onChange={handleFormChange}>
              {WORK_MODES.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </label>
          <label>
            Salary min (USD)
            <input name="salary_min" type="number" min="0" value={form.salary_min} onChange={handleFormChange} />
          </label>
          <label>
            Salary max (USD)
            <input name="salary_max" type="number" min="0" value={form.salary_max} onChange={handleFormChange} />
          </label>
          <label>
            Status
            <select name="status" value={form.status} onChange={handleFormChange}>
              {STATUSES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>
          <label>
            Date applied
            <input name="date_applied" type="date" value={form.date_applied} onChange={handleFormChange} />
          </label>
          <label>
            Follow-up date
            <input name="follow_up_date" type="date" value={form.follow_up_date} onChange={handleFormChange} />
          </label>
          <label>
            Job posting URL
            <input name="job_url" type="url" placeholder="https://…" value={form.job_url} onChange={handleFormChange} />
          </label>
          <label className="wide">
            Notes
            <textarea name="notes" rows="2" value={form.notes} onChange={handleFormChange} />
          </label>
          <div className="form-actions">
            <button type="submit">{editingId ? "Save changes" : "Add application"}</button>
            {editingId && (
              <button
                type="button"
                className="secondary"
                onClick={() => { setEditingId(null); setForm(EMPTY_FORM); }}
              >
                Cancel edit
              </button>
            )}
          </div>
        </form>
      </section>

      <section className="panel">
        <div className="list-header">
          <h2>Applications</h2>
          <div className="filters">
            <input
              type="search"
              placeholder="Search company…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All statuses</option>
              {STATUSES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <select value={workModeFilter} onChange={(e) => setWorkModeFilter(e.target.value)}>
              <option value="">All work modes</option>
              {WORK_MODES.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <p>Loading…</p>
        ) : applications.length === 0 ? (
          <p>No applications match. Add one above, or run the seed script for sample data.</p>
        ) : (
          <table className="apps-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Role</th>
                <th>Location</th>
                <th>Mode</th>
                <th>Salary</th>
                <th>Status</th>
                <th>Applied</th>
                <th>Follow-up</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {applications.map((app) => (
                <tr key={app.id}>
                  <td>
                    {app.job_url ? (
                      <a href={app.job_url} target="_blank" rel="noreferrer">{app.company}</a>
                    ) : (
                      app.company
                    )}
                  </td>
                  <td>{app.role_title}</td>
                  <td>{app.location}</td>
                  <td>{app.work_mode}</td>
                  <td>{formatSalary(app)}</td>
                  <td>
                    <span className={`badge status-${app.status}`}>{app.status}</span>
                  </td>
                  <td>{app.date_applied ?? "—"}</td>
                  <td>{app.follow_up_date ?? "—"}</td>
                  <td className="row-actions">
                    <button className="secondary" onClick={() => startEdit(app)}>Edit</button>
                    <button className="danger" onClick={() => handleDelete(app)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
