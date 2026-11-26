// Client state. The server is authoritative: this only mirrors what the API returned,
// plus purely client-side UI state (selection, playback, job progress). No localStorage.

/**
 * @typedef {{t: number, p: number, d: number, v: number}} Note
 * @typedef {{root: number, quality: string, pitch_class_set: number[], symbol: string}} Chord
 * @typedef {{id: number, role: string, program: number, name: string, mute: boolean, solo: boolean, position: number}} Track
 * @typedef {{id: number, name: string, bars: number, chord_grid: Chord[], slots: Record<string, number>}} Section
 * @typedef {{id: number, name: string, bpm: number, ts_numerator: number, ts_denominator: number, key_tonic: number, key_mode: string, genre: string, chord_grid: Chord[], tracks: Track[], sections: Section[], arrangement: number[]}} Project
 * @typedef {{id: number, track_id: number, bars: number, locked: boolean, current_version: {notes: Note[], score: number|null, seed: number|null} | null}} Clip
 * @typedef {{jobId: string, status: string, detail: Record<string, any>}} JobState
 * @typedef {{id: string, name: string, format: string, size: number, active: boolean}} Bank
 * @typedef {{active: string | null, banks: Bank[], default: {id: string, name: string, licence: string, licence_url: string}, suggested: Array<{name: string, licence: string, licence_kind: string, url: string}>}} Soundfonts
 * @typedef {{
 *   projects: Array<{id: number, name: string}>,
 *   project: Project | null,
 *   clips: Record<number, Clip>,
 *   jobs: Record<string, JobState>,
 *   selected: number,
 *   loop: boolean,
 *   playing: null | "section" | "all",
 *   playFromBar: number,
 *   zoom: number,
 *   soundfonts: Soundfonts | null,
 *   soundBusy: string,
 *   message: string,
 * }} State
 */

/** @type {State} */
const state = {
  projects: [],
  project: null,
  clips: {},
  jobs: {},
  selected: 0,
  loop: true,
  playing: null,
  playFromBar: 0,
  zoom: 56,
  soundfonts: null,
  soundBusy: "",
  message: "",
};

/** @type {Set<(s: State) => void>} */
const listeners = new Set();

/** @returns {State} */
export function getState() {
  return state;
}

/** @param {Partial<State>} patch */
export function setState(patch) {
  Object.assign(state, patch);
  for (const fn of listeners) fn(state);
}

/** @param {(s: State) => void} fn @returns {() => void} */
export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

/** @param {number} sectionId @param {number} trackId */
export function jobKey(sectionId, trackId) {
  return `${sectionId}:${trackId}`;
}
