// Thin client for the REST API (all JSON, prefix /api).

export class ApiError extends Error {
  /** @param {number} status @param {string} message */
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

/** FastAPI errors: {detail: string} or {detail: [{msg, loc}]}. @param {any} body */
function detailMessage(body) {
  const detail = body?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg ?? String(d)).join("; ");
  return "";
}

/**
 * @param {string} method
 * @param {string} path
 * @param {unknown} [body]
 * @returns {Promise<any>}
 */
export async function request(method, path, body) {
  const response = await fetch(`/api${path}`, {
    method,
    headers: body === undefined ? {} : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(response.status, detailMessage(data) || `HTTP ${response.status}`);
  }
  return data;
}

export const api = {
  health: () => request("GET", "/health"),
  listProjects: () => request("GET", "/projects"),
  getProject: (/** @type {number} */ id) => request("GET", `/projects/${id}`),
  createProject: (/** @type {object} */ data) => request("POST", "/projects", data),
  patchProject: (/** @type {number} */ id, /** @type {object} */ data) =>
    request("PATCH", `/projects/${id}`, data),
  projectClips: (/** @type {number} */ id) => request("GET", `/projects/${id}/clips`),
  addTrack: (/** @type {number} */ projectId, /** @type {object} */ data) =>
    request("POST", `/projects/${projectId}/tracks`, data),
  patchTrack: (/** @type {number} */ id, /** @type {object} */ data) =>
    request("PATCH", `/tracks/${id}`, data),
  addSection: (/** @type {number} */ projectId, /** @type {object} */ data) =>
    request("POST", `/projects/${projectId}/sections`, data),
  generate: (/** @type {object} */ data) => request("POST", "/generate", data),
  cancelJob: (/** @type {string} */ id) => request("POST", `/jobs/${id}/cancel`),
};

export const TERMINAL_EVENTS = ["done", "error", "cancelled"];

/**
 * Follow a job's Server-Sent Events until it finishes.
 * @param {string} jobId
 * @param {(event: string, data: any) => void} onEvent
 * @returns {() => void} close function
 */
export function followJob(jobId, onEvent) {
  const source = new EventSource(`/api/jobs/${jobId}/events`);
  const names = ["queued", "started", "sampling", "candidate", ...TERMINAL_EVENTS];
  for (const name of names) {
    source.addEventListener(name, (e) => {
      const data = JSON.parse(/** @type {MessageEvent} */ (e).data || "{}");
      if (TERMINAL_EVENTS.includes(name)) source.close();
      onEvent(name, data);
    });
  }
  source.onerror = () => {
    // The server closes the stream after a terminal event; anything else is a lost connection.
    if (source.readyState === EventSource.CLOSED) return;
    source.close();
    onEvent("error", { message: "connection lost" });
  };
  return () => source.close();
}
