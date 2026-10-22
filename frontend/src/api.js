// Small client for the Job Application Tracker API.
// In development, Vite proxies these paths to the FastAPI backend.
// Set VITE_API_BASE to point at a separately hosted API if needed.
const API_BASE = import.meta.env.VITE_API_BASE || "";

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
