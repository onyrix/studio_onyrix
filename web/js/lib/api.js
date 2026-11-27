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
  patchSection: (/** @type {number} */ id, /** @type {object} */ data) =>
    request("PATCH", `/sections/${id}`, data),
  harmonyDiatonic: (/** @type {number} */ tonic, /** @type {string} */ mode) =>
    request("GET", `/harmony/diatonic?tonic=${tonic}&mode=${encodeURIComponent(mode)}`),
  harmonySuggest: (/** @type {object} */ data) => request("POST", "/harmony/suggest", data),
  harmonyNext: (/** @type {object} */ data) => request("POST", "/harmony/next", data),
  harmonyParse: (/** @type {object} */ data) => request("POST", "/harmony/parse", data),
  kits: (/** @type {number} */ projectId, /** @type {string[]} */ moods) =>
    request(
      "GET",
      `/harmony/kits?${new URLSearchParams([["project_id", String(projectId)], ...moods.map((m) => ["moods", m])])}`,
    ),
  applyKit: (/** @type {object} */ data) => request("POST", "/harmony/kits/apply", data),
  harmonyOperators: () => request("GET", "/harmony/operators"),
  harmonyTransform: (/** @type {object} */ data) => request("POST", "/harmony/transform", data),
  harmonyExplore: (/** @type {object} */ data) => request("POST", "/harmony/explore", data),
  harmonyPrompt: (/** @type {object} */ data) => request("POST", "/harmony/prompt", data),
  llmStatus: () => request("GET", "/llm/status"),
  corpus: () => request("GET", "/corpus"),
  corpusDownload: () => request("POST", "/corpus/download"),
  corpusDelete: () => request("DELETE", "/corpus"),
  generate: (/** @type {object} */ data) => request("POST", "/generate", data),
  cancelJob: (/** @type {string} */ id) => request("POST", `/jobs/${id}/cancel`),
  soundfonts: () => request("GET", "/soundfonts"),
  setActiveSoundfont: (/** @type {string} */ id) => request("PUT", "/soundfonts/active", { id }),
  deleteSoundfont: (/** @type {string} */ id) =>
    request("DELETE", `/soundfonts/${encodeURIComponent(id)}`),
  downloadDefaultSoundfont: () => request("POST", "/soundfonts/default"),
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

/**
 * Upload a sound bank as the raw request body, reporting progress (fetch has no upload progress).
 * @param {File} file
 * @param {(fraction: number) => void} onProgress
 * @returns {Promise<any>}
 */
export function uploadSoundfont(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `/api/soundfonts?filename=${encodeURIComponent(file.name)}`);
    xhr.setRequestHeader("Content-Type", "application/octet-stream");
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) onProgress(e.loaded / e.total);
    };
    xhr.onload = () => {
      const body = (() => {
        try {
          return JSON.parse(xhr.responseText);
        } catch {
          return null;
        }
      })();
      if (xhr.status >= 200 && xhr.status < 300) resolve(body);
      else reject(new ApiError(xhr.status, detailMessage(body) || `HTTP ${xhr.status}`));
    };
    xhr.onerror = () => reject(new ApiError(0, "network error"));
    xhr.send(file);
  });
}