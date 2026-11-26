// Browser playback with SpessaSynth (vendored, Apache-2.0) and a SoundFont/DLS bank.
// The browser plays the very MIDI file the server exports (same notes, tempo, programs and
// channels as the DAW export), so what you hear is what you get. Mute/solo mute MIDI channels.
// SpessaSynth is imported lazily on the first play to keep page load light.

/** @typedef {import("./store.js").Project} Project */
/** @typedef {import("./store.js").Track} Track */

const PROCESSOR_URL = "/vendor/spessasynth/spessasynth_processor.min.js";
const DRUM_CHANNEL = 9;

/** @type {AudioContext | null} */
let ctx = null;
/** @type {any} */
let synth = null;
/** @type {any} */
let sequencer = null;
/** @type {string | null} */
let loadedBank = null;
let playing = false;
/** @type {() => void} */
let onStopped = () => {};

/** Register a callback fired whenever playback stops. @param {() => void} fn */
export function onStop(fn) {
  onStopped = fn;
}

/**
 * MIDI channel of each track, mirroring app/midi_io.py `_channels`: drums on channel 10
 * (index 9), melodic tracks take the other channels in track order.
 * @param {Track[]} tracks  in position order
 * @returns {Map<number, number>} track id -> channel
 */
export function channelMap(tracks) {
  const melodic = Array.from({ length: 16 }, (_, c) => c).filter((c) => c !== DRUM_CHANNEL);
  const out = new Map();
  let next = 0;
  for (const track of tracks) {
    if (track.role === "drums") out.set(track.id, DRUM_CHANNEL);
    else out.set(track.id, melodic[next++ % melodic.length]);
  }
  return out;
}

/** Tracks that should sound: solo wins over mute. @param {Track[]} tracks */
export function audibleTracks(tracks) {
  const soloed = tracks.filter((t) => t.solo);
  return soloed.length ? soloed : tracks.filter((t) => !t.mute);
}

async function ensureSynth() {
  if (!ctx) {
    const { WorkletSynthesizer, Sequencer } = await import("spessasynth_lib");
    ctx = new AudioContext();
    await ctx.audioWorklet.addModule(PROCESSOR_URL);
    synth = new WorkletSynthesizer(ctx);
    synth.connect(ctx.destination);
    sequencer = new Sequencer(synth, { skipToFirstNoteOn: false, initialPlaybackRate: 1 });
    sequencer.eventHandler.addEvent("songEnded", "onyrix", () => {
      if (sequencer.loopCount === 0) markStopped();
    });
  }
  await ctx.resume();
}

/** @param {string} bankId */
async function ensureBank(bankId) {
  if (loadedBank === bankId) return;
  const response = await fetch(`/api/soundfonts/${encodeURIComponent(bankId)}/file`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const buffer = await response.arrayBuffer();
  await synth.soundBankManager.addSoundBank(buffer, "main");
  await synth.isReady;
  loadedBank = bankId;
}

function markStopped() {
  if (!playing) return;
  playing = false;
  onStopped();
}

/** Apply mute/solo to the synth's channels (safe to call while playing). @param {Track[]} tracks */
export function applyMutes(tracks) {
  if (!synth) return;
  const channels = channelMap(tracks);
  const audible = new Set(audibleTracks(tracks).map((t) => t.id));
  for (const [trackId, channel] of channels) {
    synth.midiChannels[channel]?.setSystemParameter("isMuted", !audible.has(trackId));
  }
}

/**
 * Play arrangement instances [first, last] of `project` with the given bank.
 * @param {Project} project
 * @param {number[]} instanceIndexes  contiguous indexes into project.arrangement
 * @param {{loop: boolean, bankId: string}} options
 * @returns {Promise<void>}
 */
export async function play(project, instanceIndexes, options) {
  await ensureSynth();
  await ensureBank(options.bankId);
  stop();
  const start = Math.min(...instanceIndexes);
  const end = Math.max(...instanceIndexes) + 1;
  const response = await fetch(
    `/api/export/project/${project.id}.mid?start=${start}&end=${end}&loop=true`,
  );
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const binary = await response.arrayBuffer();
  sequencer.loopCount = options.loop ? Infinity : 0;
  sequencer.loadNewSongList([{ binary, fileName: `${project.name}.mid` }]);
  applyMutes([...project.tracks].sort((a, b) => a.position - b.position));
  sequencer.currentTime = 0;
  sequencer.play();
  playing = true;
}

export function stop() {
  if (sequencer) {
    sequencer.pause();
    synth.stopAll(true);
  }
  markStopped();
}

/** Current position in seconds within the played range (0 when stopped). */
export function positionSeconds() {
  return playing && sequencer ? Math.max(0, sequencer.currentTime) : 0;
}

export function isPlaying() {
  return playing;
}

/** Forget the loaded bank (e.g. after it was deleted or replaced). */
export function resetBank() {
  loadedBank = null;
}
