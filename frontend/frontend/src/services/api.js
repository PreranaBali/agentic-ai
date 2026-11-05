// All backend calls live here. The Groq key never reaches the browser: only the backend has it.
const BASE = 'https://agentic-ai-elhx.onrender.com';

export class ApiError extends Error {
  constructor(message, code, status) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

async function request(path, { method = 'GET', body, params } = {}) {
  const url = new URL(BASE + path);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v);
    });
  }
  let res;
  try {
    res = await fetch(url, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(`Can't reach the backend at ${BASE}. Check that it's running.`, 'network', 0);
  }
  if (res.status === 204) return null;
  let data = null;
  try {
    data = await res.json();
  } catch {
    /* non-JSON body */
  }
  if (!res.ok) {
    let message = data?.error?.message;
    if (!message && Array.isArray(data?.detail)) {
      message = data.detail.map((d) => `${(d.loc || []).slice(1).join('.')}: ${d.msg}`).join('; ');
    }
    throw new ApiError(message || `Request failed (${res.status})`, data?.error?.code || `http_${res.status}`, res.status);
  }
  return data;
}

export const api = {
  baseUrl: BASE,
  health: () => request('/api/health'),
  providerStatus: () => request('/api/provider/status'),
  providerModels: () => request('/api/provider/models'),
  stats: () => request('/api/stats'),
  agentStatus: () => request('/api/agent/status'),
  listRequests: (params) => request('/api/requests', { params }),
  getRequest: (id) => request(`/api/requests/${id}`),
  createRequest: (body) => request('/api/requests', { method: 'POST', body }),
  updateStatus: (id, status, note = '') =>
    request(`/api/requests/${id}/status`, { method: 'PATCH', body: { status, note } }),
  deleteRequest: (id) => request(`/api/requests/${id}`, { method: 'DELETE' }),
  analyze: (id) => request(`/api/requests/${id}/analyze`, { method: 'POST' }),
  decisions: (params) => request('/api/decisions', { params }),
};
