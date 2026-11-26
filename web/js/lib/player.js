// Browser playback with Tone.js (vendored UMD build, global `Tone`).
// Notes are scheduled on Tone.Transport, converting ticks to seconds from the project tempo.
// Mute/solo are applied here, client-side. Timbres are Tone's built-in synths per role
// (a General MIDI SoundFont synth is a later step).

import { barTicks, ticksToSeconds } from "./timebase.js";

/** @type {any} */
const Tone = /** @type {any} */ (globalThis).Tone;

/** @typedef {import("./store.js").Project} Project */
/** @typedef {import("./store.js").Clip} Clip */
/** @typedef {import("./store.js").Track} Track */

/** @type {Map<number, {role: string, trigger: (pitch: number, dur: number, time: number, vel: number) => void, dispose: () => void}>} */
const instruments = new Map();

/** @param {number} midi */
const freq = (midi) => Tone.Frequency(midi, "midi").toFrequency();

function makeDrums() {
  const out = new Tone.Volume(-6).toDestination();
  const kick = new Tone.MembraneSynth({ pitchDecay: 0.03, octaves: 6 }).connect(out);
  const tom = new Tone.MembraneSynth({ pitchDecay: 0.02, octaves: 3 }).connect(out);
  const snare = new Tone.NoiseSynth({
    noise: { type: "white" },
    envelope: { attack: 0.001, decay: 0.15, sustain: 0 },
  }).connect(out);
  const hat = new Tone.MetalSynth({
    envelope: { attack: 0.001, decay: 0.06, release: 0.01 },
    harmonicity: 5.1,
    modulationIndex: 32,
    resonance: 4000,
    octaves: 1.5,
  }).connect(new Tone.Volume(-14).connect(out));
  const parts = [out, kick, tom, snare, hat];
  return {
    /** @param {number} pitch @param {number} dur @param {number} time @param {number} vel */
    trigger(pitch, dur, time, vel) {
      if (pitch === 35 || pitch === 36) kick.triggerAttackRelease("C1", "16n", time, vel);
      else if (pitch >= 37 && pitch <= 40) snare.triggerAttackRelease("16n", time, vel);
      else if ([41, 43, 45, 47, 48, 50].includes(pitch))
        tom.triggerAttackRelease(freq(pitch - 12), "16n", time, vel);
      else {
        const long = [46, 49, 51, 52, 55, 57, 59].includes(pitch);
        hat.triggerAttackRelease(long ? "8n" : "32n", time, vel * 0.8);
      }
    },
    dispose: () => parts.forEach((p) => p.dispose()),
  };
}

/** @param {string} role */
function makeMelodic(role) {
  const out = new Tone.Volume(-10).toDestination();
  let synth;
  if (role === "bass") {
    synth = new Tone.MonoSynth({
      oscillator: { type: "sawtooth" },
      filter: { Q: 2, type: "lowpass" },
      filterEnvelope: { attack: 0.005, decay: 0.2, sustain: 0.3, baseFrequency: 120, octaves: 2.5 },
      envelope: { attack: 0.005, decay: 0.2, sustain: 0.6, release: 0.1 },
    });
  } else if (role === "lead") {
    synth = new Tone.MonoSynth({
      oscillator: { type: "square" },
      envelope: { attack: 0.01, decay: 0.1, sustain: 0.5, release: 0.2 },
      filterEnvelope: { baseFrequency: 600, octaves: 3 },
    });
  } else if (role === "pad") {
    synth = new Tone.PolySynth(Tone.AMSynth, {
      envelope: { attack: 0.4, decay: 0.3, sustain: 0.7, release: 1.2 },
    });
  } else {
    synth = new Tone.PolySynth(Tone.Synth, {
      oscillator: { type: "triangle" },
      envelope: { attack: 0.01, decay: 0.3, sustain: 0.4, release: 0.6 },
    });
  }
  synth.connect(out);
  return {
    /** @param {number} pitch @param {number} dur @param {number} time @param {number} vel */
    trigger(pitch, dur, time, vel) {
      synth.triggerAttackRelease(freq(pitch), dur, time, vel);
    },
    dispose: () => {
      synth.dispose();
      out.dispose();
    },
  };
}

/** @param {Track} track */
function instrumentFor(track) {
  const existing = instruments.get(track.id);
  if (existing && existing.role === track.role) return existing;
  existing?.dispose();
  const made = track.role === "drums" ? makeDrums() : makeMelodic(track.role);
  const entry = { role: track.role, ...made };
  instruments.set(track.id, entry);
  return entry;
}

/** Tracks that should sound: solo wins over mute. @param {Track[]} tracks */
export function audibleTracks(tracks) {
  const soloed = tracks.filter((t) => t.solo);
  return soloed.length ? soloed : tracks.filter((t) => !t.mute);
}

/**
 * Schedule a list of section instances (by index into project.arrangement) and start.
 * @param {Project} project
 * @param {Record<number, Clip>} clips
 * @param {number[]} instanceIndexes
 * @param {{loop: boolean}} options
 * @returns {Promise<number>} total length in seconds (0 = nothing to play)
 */
export async function play(project, clips, instanceIndexes, options) {
  await Tone.start();
  stop();
  const transport = Tone.getTransport();
  transport.bpm.value = project.bpm;
  const bar = barTicks(project.ts_numerator, project.ts_denominator);
  const sections = new Map(project.sections.map((s) => [s.id, s]));
  const tracks = audibleTracks(project.tracks);

  let offset = 0;
  let scheduled = 0;
  for (const index of instanceIndexes) {
    const section = sections.get(project.arrangement[index]);
    if (!section) continue;
    const length = section.bars * bar;
    for (const track of tracks) {
      const clip = clips[section.slots[String(track.id)]];
      const notes = clip?.current_version?.notes ?? [];
      if (!notes.length) continue;
      const instrument = instrumentFor(track);
      for (const note of notes) {
        if (note.t >= length) continue;
        const start = ticksToSeconds(offset + note.t, project.bpm);
        const dur = ticksToSeconds(Math.min(note.d, length - note.t), project.bpm);
        const vel = note.v / 127;
        transport.schedule((/** @type {number} */ time) => {
          instrument.trigger(note.p, dur, time, vel);
        }, start);
        scheduled += 1;
      }
    }
    offset += length;
  }
  const total = ticksToSeconds(offset, project.bpm);
  if (!scheduled) return 0;
  transport.loop = options.loop;
  transport.loopStart = 0;
  transport.loopEnd = total;
  if (!options.loop) transport.scheduleOnce(() => stop(), total + 0.05);
  transport.start("+0.05", 0);
  return total;
}

/** @type {() => void} */
let onStopped = () => {};

/** Register a callback fired whenever playback stops. @param {() => void} fn */
export function onStop(fn) {
  onStopped = fn;
}

export function stop() {
  const transport = Tone.getTransport();
  const wasPlaying = transport.state === "started";
  transport.stop();
  transport.cancel(0);
  transport.loop = false;
  if (wasPlaying) onStopped();
}

/** Current transport position in seconds (0 when stopped). */
export function positionSeconds() {
  const transport = Tone.getTransport();
  return transport.state === "started" ? transport.seconds : 0;
}

export function isPlaying() {
  return Tone.getTransport().state === "started";
}
