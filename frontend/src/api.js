// Small client for the Job Application Tracker API.
// In development, Vite proxies these paths to the FastAPI backend, so
// relative URLs are used. In production builds, set VITE_API_URL to the
// API's absolute base URL (the legacy VITE_API_BASE name still works).
const API_BASE = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE ||
  ""
).replace(/\/$/, "");

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* keep statusText */
    }
    throw new Error(`${response.status}: ${detail}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

export function listApplications({ status, company, workMode } = {}) {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (company) params.set("company", company);
  if (workMode) params.set("work_mode", workMode);
  const query = params.toString();
  return request(`/applications${query ? `?${query}` : ""}`);
}

export function getStats() {
  return request("/stats");
}

export function createApplication(data) {
  return request("/applications", { method: "POST", body: JSON.stringify(data) });
}

export function updateApplication(id, data) {
  return request(`/applications/${id}`, { method: "PATCH", body: JSON.stringify(data) });
}

export function deleteApplication(id) {
  return request(`/applications/${id}`, { method: "DELETE" });
}
