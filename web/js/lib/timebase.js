// Mirror of app/core/timebase.py (the tested reference). Ticks are the only stored unit.

export const PPQ = 480;
export const STEP_TICKS = PPQ / 4;

/** @param {number} numerator @param {number} denominator */
export function barTicks(numerator = 4, denominator = 4) {
  return (numerator * PPQ * 4) / denominator;
}

/** Playback-only conversion at a constant tempo. @param {number} ticks @param {number} bpm */
export function ticksToSeconds(ticks, bpm) {
  return ((ticks / PPQ) * 60) / bpm;
}

/** @param {number} seconds @param {number} bpm */
export function secondsToTicks(seconds, bpm) {
  return (seconds * bpm * PPQ) / 60;
}
