// Actions: call the API, then mirror the server's answer into the store.

import { api, followJob, uploadSoundfont as uploadBank } from "./api.js";
import { t } from "./i18n.js";
import { resetBank } from "./player.js";
import { getState, jobKey, setState } from "./store.js";

/** @param {unknown} error */
export function showError(error) {
  const message = error instanceof Error ? error.message : String(error);
  setState({ message: t("error.generic", { message }) });
}

export async function loadProjects() {
  setState({ projects: await api.listProjects() });
}

/** Reload the open project and all its clips from the server. */
export async function refreshProject() {
  const current = getState().project;
  if (!current) return;
  const [project, clipList] = await Promise.all([
    api.getProject(current.id),
    api.projectClips(current.id),
  ]);
  /** @type {Record<number, any>} */
  const clips = {};
  for (const clip of clipList) clips[clip.id] = clip;
  const selected = Math.min(getState().selected, Math.max(0, project.arrangement.length - 1));
  setState({ project, clips, selected });
}

/** @param {number} id */
export async function openProject(id) {
  const [project, clipList] = await Promise.all([api.getProject(id), api.projectClips(id)]);
  /** @type {Record<number, any>} */
  const clips = {};
  for (const clip of clipList) clips[clip.id] = clip;
  setState({ project, clips, selected: 0, jobs: {}, message: "" });
}

/** Split "Am F, C  G" into ["Am", "F", "C", "G"]. @param {string} text */
export function parseChords(text) {
  return text
    .split(/[\s,]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

/** @param {object} data */
export async function createProject(data) {
  const project = await api.createProject(data);
  await loadProjects();
  await openProject(project.id);
}

/** @param {object} data */
export async function updateProject(data) {
  const project = getState().project;
  if (!project) return;
  await api.patchProject(project.id, data);
  await Promise.all([refreshProject(), loadProjects()]);
}

/** @param {object} data */
export async function addTrack(data) {
  const project = getState().project;
  if (!project) return;
  await api.addTrack(project.id, data);
  await refreshProject();
}

/** @param {number} trackId @param {object} data */
export async function patchTrack(trackId, data) {
  await api.patchTrack(trackId, data);
  await refreshProject();
}

/** @param {object} data */
export async function addSection(data) {
  const project = getState().project;
  if (!project) return;
  await api.addSection(project.id, data);
  await refreshProject();
}

/** @param {number} sectionId @param {object} data */
export async function patchSection(sectionId, data) {
  await api.patchSection(sectionId, data);
  await refreshProject();
}

/** @param {string} key @param {Partial<import("./store.js").JobState>} patch */
function updateJob(key, patch) {
  const jobs = { ...getState().jobs };
  jobs[key] = /** @type {any} */ ({ ...jobs[key], ...patch });
  setState({ jobs });
}

/** Start a generation for one cell and follow its progress. @param {number} sectionId @param {number} trackId */
export async function generate(sectionId, trackId) {
  const key = jobKey(sectionId, trackId);
  const job = await api.generate({ section_id: sectionId, track_id: trackId });
  updateJob(key, { jobId: job.id, status: "queued", detail: {} });
  let candidates = 0;
  let total = 0;
  followJob(job.id, (event, data) => {
    if (event === "sampling") total = data.n_candidates ?? 0;
    if (event === "candidate") candidates += 1;
    updateJob(key, { status: event, detail: { ...data, count: candidates, total } });
    if (event === "done") refreshProject().catch(showError);
  });
}

/** @param {number} sectionId @param {number} trackId */
export async function cancel(sectionId, trackId) {
  const job = getState().jobs[jobKey(sectionId, trackId)];
  if (job) await api.cancelJob(job.jobId);
}

// ---- Sound banks -------------------------------------------------------------------------

export async function loadSoundfonts() {
  setState({ soundfonts: await api.soundfonts() });
}

/** Run a bank operation with a busy label, then refresh the list. @param {string} label @param {() => Promise<unknown>} task */
async function withSoundBusy(label, task) {
  setState({ soundBusy: label });
  try {
    await task();
    resetBank();
    await loadSoundfonts();
  } finally {
    setState({ soundBusy: "" });
  }
}

/** @param {File} file */
export function importSoundfont(file) {
  return withSoundBusy(t("sound.uploading", { percent: 0 }), () =>
    uploadBank(file, (fraction) =>
      setState({ soundBusy: t("sound.uploading", { percent: Math.round(fraction * 100) }) }),
    ),
  );
}

export function downloadDefaultSoundfont() {
  return withSoundBusy(t("sound.downloading"), () => api.downloadDefaultSoundfont());
}

/** @param {string} id */
export function setActiveSoundfont(id) {
  return withSoundBusy(t("sound.switching"), () => api.setActiveSoundfont(id));
}

/** @param {string} id */
export function deleteSoundfont(id) {
  return withSoundBusy(t("sound.deleting"), () => api.deleteSoundfont(id));
}
