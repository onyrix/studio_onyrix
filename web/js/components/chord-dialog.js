// Chord dialog: edit one section's progression as chord events with durations (harmonic
// rhythm), with suggested progressions, the key's diatonic chords and chord changes for the
// selected chord. Parsing and spelling happen on the server (core/progression.py is the tested
// reference); `eventsText` below mirrors its `progression_text`.

import { audition, patchSection, showError } from "../lib/actions.js";
import { api } from "../lib/api.js";
import { h } from "../lib/dom.js";
import { t } from "../lib/i18n.js";
import { getState } from "../lib/store.js";
import { explorerPanel, initExplorer, loadExplorer, meter, refreshInfo } from "./explorer.js";

/**
 * @typedef {{symbol: string, numeral: string}} ChordInfo
 * @typedef {{symbol: string, beats: number}} Event
 * @typedef {{
 *   sectionId: number, selected: number, events: Event[], inherited: boolean,
 *   diatonic: ChordInfo[],
 *   progressions: Array<{id: string, chords: Array<ChordInfo & {beats: number}>, chord_text: string, numerals: string, moods: string[], surprise_level: number}>,
 *   moods: string[],
 *   next: Array<ChordInfo & {kind: string}>, kind: string, error: string,
 *   typed: string | null,
 * }} Local
 */

/** Mood tags of the progression library (mirror of core/library.py MOODS). */
export const MOODS = [
  "bright",
  "uplifting",
  "melancholic",
  "nostalgic",
  "dreamy",
  "romantic",
  "dark",
  "epic",
  "tense",
  "mysterious",
  "groovy",
  "calm",
];

/** @type {Local | null} */
let local = null;

const dialog = () => /** @type {HTMLDialogElement} */ (document.getElementById("dialog-chords"));
const body = () => /** @type {HTMLElement} */ (document.getElementById("chords-body"));

function section() {
  const project = getState().project;
  return project?.sections.find((s) => s.id === local?.sectionId);
}

function beatsPerBar() {
  return getState().project?.ts_numerator ?? 4;
}

/** Canonical progression text (mirror of core/progression.py `progression_text`). @param {Event[]} events */
export function eventsText(events) {
  const perBar = beatsPerBar();
  const out = [];
  let i = 0;
  while (i < events.length) {
    const { symbol, beats } = events[i];
    if (beats < perBar && perBar % beats === 0) {
      const n = perBar / beats;
      const group = events.slice(i, i + n);
      if (group.length === n && group.every((e) => e.beats === beats)) {
        out.push(`(${group.map((e) => e.symbol).join(" ")})`);
        i += n;
        continue;
      }
    }
    if (beats === perBar) out.push(symbol);
    else if (beats % perBar === 0) out.push(`${symbol}*${beats / perBar}`);
    else out.push(`${symbol}:${beats}`);
    i += 1;
  }
  return out.join(" ");
}

/** @param {Array<{symbol: string, beats?: number}>} grid @returns {Event[]} */
function toEvents(grid) {
  return grid.map((c) => ({ symbol: c.symbol, beats: c.beats ?? beatsPerBar() }));
}

/**
 * @param {number} sectionId
 * @param {number} eventIndex  index in the section's progression (not in the cycled timeline)
 */
export async function openChordDialog(sectionId, eventIndex) {
  const project = getState().project;
  const target = project?.sections.find((s) => s.id === sectionId);
  if (!project || !target) return;
  const inherited = !target.chord_grid.length;
  const events = toEvents(inherited ? project.chord_grid : target.chord_grid);
  local = {
    sectionId,
    selected: Math.min(eventIndex, Math.max(0, events.length - 1)),
    events,
    inherited,
    diatonic: [],
    progressions: [],
    moods: [],
    next: [],
    kind: "",
    error: "",
    typed: null,
  };
  initExplorer(render);
  render();
  if (!dialog().open) dialog().showModal();
  loadExplorer();
  try {
    const diatonic = await api.harmonyDiatonic(project.key_tonic, project.key_mode);
    if (!local || local.sectionId !== sectionId) return;
    local.diatonic = diatonic;
    render();
  } catch (e) {
    showError(e);
  }
  await Promise.all([loadSuggestions(), loadNext()]);
}

/** Library progressions for this section, filtered by the selected moods. */
async function loadSuggestions() {
  const project = getState().project;
  if (!local || !project) return;
  const { sectionId, moods } = local;
  try {
    const suggested = await api.harmonySuggest({
      project_id: project.id,
      section_id: sectionId,
      moods,
      n: 12,
    });
    if (!local || local.sectionId !== sectionId || local.moods !== moods) return;
    local.progressions = suggested.progressions;
    local.kind = suggested.section_kind;
    render();
  } catch (e) {
    showError(e);
  }
}

/** @param {string} mood */
function toggleMood(mood) {
  if (!local) return;
  local.moods = local.moods.includes(mood)
    ? local.moods.filter((m) => m !== mood)
    : [...local.moods, mood];
  render();
  loadSuggestions();
}

/** @param {string} text */
function listen(text) {
  audition(text).catch(showError);
}

/** Chord changes suggested after the chord preceding the selected one (cyclic). */
async function loadNext() {
  const project = getState().project;
  if (!local || !project || !local.events.length) return;
  const n = local.events.length;
  const at = local.selected;
  const prev = local.events[(at - 1 + n) % n].symbol;
  try {
    const next = await api.harmonyNext({ project_id: project.id, chord: prev });
    if (local && local.selected === at) {
      local.next = next;
      render();
    }
  } catch {
    if (local) {
      local.next = [];
      render();
    }
  }
}

/** Apply a change to the events, mark the grid as the section's own and re-render. @param {(events: Event[]) => void} change */
function update(change) {
  if (!local) return;
  change(local.events);
  local.inherited = false;
  local.error = "";
  local.typed = null;
  local.selected = Math.max(0, Math.min(local.selected, local.events.length - 1));
  render();
}

/** Put a chord on the selected event, keeping its duration, then move on. @param {string} symbol */
function setChord(symbol) {
  if (!local) return;
  update((events) => {
    if (!events.length) events.push({ symbol, beats: beatsPerBar() });
    else events[/** @type {Local} */ (local).selected].symbol = symbol;
  });
  if (local.selected < local.events.length - 1) local.selected += 1;
  render();
  loadNext();
}

/** @param {number} index */
function select(index) {
  if (!local) return;
  local.selected = index;
  render();
  loadNext();
}

/** Duration presets in beats for the current time signature. */
function durations() {
  const perBar = beatsPerBar();
  /** @type {Array<[string, number]>} */
  const out = [[t("chords.dur.beat"), 1]];
  if (perBar % 2 === 0) out.push([t("chords.dur.half"), perBar / 2]);
  out.push([t("chords.dur.bar"), perBar], [t("chords.dur.bars", { n: 2 }), 2 * perBar]);
  out.push([t("chords.dur.bars", { n: 4 }), 4 * perBar]);
  return out;
}

/** @param {string} text */
async function parseText(text) {
  const project = getState().project;
  if (!local || !project) return;
  try {
    const parsed = await api.harmonyParse({ project_id: project.id, text });
    update((events) => {
      events.splice(0, events.length, ...parsed.events.map((/** @type {any} */ e) => ({ symbol: e.symbol, beats: e.beats })));
    });
  } catch (e) {
    local.error = e instanceof Error ? e.message : String(e);
    render();
  }
}

/** @param {boolean} useProject  true = back to the project's progression */
async function save(useProject) {
  if (!local) return;
  try {
    // Text typed but not parsed yet (Save clicked right after typing) goes to the server as is.
    const text = local.typed ?? eventsText(local.events);
    const grid = useProject || (local.inherited && local.typed === null) ? [] : text;
    await patchSection(local.sectionId, { chord_grid: grid });
    dialog().close();
    local = null;
  } catch (e) {
    local.error = e instanceof Error ? e.message : String(e);
    render();
  }
}

/** @param {ChordInfo} chord @param {string} [extra] */
function chip(chord, extra) {
  return h(
    "button.chip",
    { type: "button", onclick: () => setChord(chord.symbol) },
    h("strong", null, chord.symbol),
    h("small", null, extra ? `${chord.numeral} · ${extra}` : chord.numeral),
  );
}

/** Human duration label for an event. @param {number} beats */
function durationLabel(beats) {
  const perBar = beatsPerBar();
  if (beats % perBar === 0) return t(beats === perBar ? "chords.dur.bar" : "chords.dur.bars", { n: beats / perBar });
  return t("chords.dur.beats", { n: beats });
}

function eventEditor() {
  const state = /** @type {Local} */ (local);
  const perBar = beatsPerBar();
  const strip = h("div.chord-events", { role: "group", "aria-label": t("chords.events") });
  state.events.forEach((event, i) => {
    const button = h(
      `button.chord-event${i === state.selected ? ".selected" : ""}${state.inherited ? ".inherited" : ""}`,
      { type: "button", "aria-pressed": String(i === state.selected), onclick: () => select(i) },
      h("span", null, event.symbol),
      h("small", null, durationLabel(event.beats)),
    );
    button.style.flexGrow = String(event.beats);
    strip.append(button);
  });
  const current = state.events[state.selected];
  const tools = current
    ? h(
        "div.chord-tools",
        null,
        h("span.muted", null, t("chords.duration")),
        ...durations().map(([label, beats]) =>
          h(
            `button.small${current.beats === beats ? ".primary" : ""}`,
            { type: "button", onclick: () => update((events) => (events[state.selected].beats = beats)) },
            label,
          ),
        ),
        h(
          "button.small",
          {
            type: "button",
            title: t("chords.splitTitle"),
            disabled: current.beats < 2,
            onclick: () =>
              update((events) => {
                const half = Math.floor(current.beats / 2);
                events.splice(state.selected, 1, { ...current, beats: current.beats - half }, { ...current, beats: half });
              }),
          },
          t("chords.split"),
        ),
        h(
          "button.small",
          {
            type: "button",
            onclick: () => update((events) => events.splice(state.selected + 1, 0, { symbol: current.symbol, beats: perBar })),
          },
          t("chords.insert"),
        ),
        h(
          "button.small",
          {
            type: "button",
            disabled: state.events.length < 2,
            onclick: () => update((events) => events.splice(state.selected, 1)),
          },
          t("chords.remove"),
        ),
      )
    : null;
  return [strip, tools];
}

function render() {
  const root = body();
  const target = section();
  if (!local || !target) {
    root.replaceChildren();
    return;
  }
  const state = local;
  const totalBeats = state.events.reduce((sum, e) => sum + e.beats, 0);
  const input = /** @type {HTMLInputElement} */ (
    h("input", {
      value: eventsText(state.events),
      placeholder: "C*2 (Am F) G:3 G7:1",
      "aria-label": t("chords.gridLabel"),
      oninput: () => {
        state.typed = input.value;
      },
      onchange: () => parseText(input.value),
    })
  );
  root.replaceChildren(
    h("h2", null, t("chords.title", { section: target.name })),
    h(
      "label",
      null,
      h("span", null, t("chords.gridLabel")),
      input,
      h("small", null, state.inherited ? t("chords.inherited") : t("chords.hint")),
    ),
    ...eventEditor(),
    h(
      "p.muted",
      null,
      t("chords.length", {
        bars: Math.round((totalBeats / beatsPerBar()) * 100) / 100,
        section: target.bars,
      }),
    ),
    explorerPanel({
      text: state.typed ?? eventsText(state.events),
      selected: state.selected,
      selectedSymbol: state.events[state.selected]?.symbol ?? "",
      sectionId: state.sectionId,
      apply: (events) =>
        update((current) => {
          current.splice(0, current.length, ...events);
        }),
      onError: (message) => {
        state.error = message;
        render();
      },
    }),
    h("h3", null, t("chords.next", { n: state.selected + 1 })),
    h("div.chips", null, ...state.next.map((c) => chip(c, t(`chords.kind.${c.kind}`)))),
    h("h3", null, t("chords.diatonic")),
    h("div.chips", null, ...state.diatonic.map((c) => chip(c))),
    h(
      "h3",
      null,
      state.kind
        ? t("chords.progressionsFor", { kind: t(`sectionKind.${state.kind}`) })
        : t("chords.progressions"),
    ),
    h(
      "div.chips.moods",
      { role: "group", "aria-label": t("chords.moods") },
      ...MOODS.map((mood) =>
        h(
          `button.small.mood${state.moods.includes(mood) ? ".primary" : ""}`,
          { type: "button", "aria-pressed": String(state.moods.includes(mood)), onclick: () => toggleMood(mood) },
          t(`mood.${mood}`),
        ),
      ),
    ),
    state.progressions.length
      ? h(
          "ul.progressions",
          null,
          ...state.progressions.map((p) =>
            h(
              "li.progression-row",
              null,
              h(
                "button.small.listen",
                { type: "button", title: t("chords.listen"), "aria-label": t("chords.listen"), onclick: () => listen(p.chord_text) },
                "▶",
              ),
              h(
                "button.progression",
                {
                  type: "button",
                  title: t("chords.use"),
                  onclick: () =>
                    update((events) =>
                      events.splice(0, events.length, ...p.chords.map((c) => ({ symbol: c.symbol, beats: c.beats }))),
                    ),
                },
                h("strong", null, p.chord_text),
                h(
                  "small",
                  null,
                  `${p.numerals} · ${p.moods.map((m) => t(`mood.${m}`)).join(", ")} `,
                  meter(p.surprise_level),
                ),
              ),
            ),
          ),
        )
      : h("p.muted", null, t("chords.noMatch")),
    h("p.form-error", { role: "alert", hidden: !state.error }, state.error),
    h(
      "footer",
      null,
      h(
        "button.listen-current",
        { type: "button", disabled: !state.events.length, onclick: () => listen(state.typed ?? eventsText(state.events)) },
        `▶ ${t("chords.listenCurrent")}`,
      ),
      h("button", { type: "button", onclick: () => save(true) }, t("chords.useProject")),
      h("button", { type: "button", onclick: () => dialog().close() }, t("form.close")),
      h("button.primary", { type: "button", onclick: () => save(false) }, t("form.save")),
    ),
  );
  if (state.events.length) refreshInfo(state.typed ?? eventsText(state.events), state.sectionId);
}
