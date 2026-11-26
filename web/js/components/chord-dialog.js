// Chord dialog: edit one section's chord grid, with suggested progressions, the key's diatonic
// chords and chord changes for the selected bar. The server validates and spells the chords.

import { patchSection, parseChords, showError } from "../lib/actions.js";
import { api } from "../lib/api.js";
import { h } from "../lib/dom.js";
import { t } from "../lib/i18n.js";
import { getState } from "../lib/store.js";

/**
 * @typedef {{symbol: string, numeral: string}} ChordInfo
 * @typedef {{
 *   sectionId: number, bar: number, tokens: string[], inherited: boolean,
 *   diatonic: ChordInfo[], progressions: Array<{chords: ChordInfo[], numerals: string}>,
 *   next: Array<ChordInfo & {kind: string}>, kind: string, error: string,
 * }} Local
 */

/** @type {Local | null} */
let local = null;

const dialog = () => /** @type {HTMLDialogElement} */ (document.getElementById("dialog-chords"));
const body = () => /** @type {HTMLElement} */ (document.getElementById("chords-body"));

function section() {
  const project = getState().project;
  return project?.sections.find((s) => s.id === local?.sectionId);
}

/** Cycle `tokens` to exactly `bars` entries (the server cycles a shorter grid the same way). */
function expand(/** @type {string[]} */ tokens, /** @type {number} */ bars) {
  if (!tokens.length) return [];
  return Array.from({ length: bars }, (_, i) => tokens[i % tokens.length]);
}

/** @param {number} sectionId @param {number} bar */
export async function openChordDialog(sectionId, bar) {
  const project = getState().project;
  const target = project?.sections.find((s) => s.id === sectionId);
  if (!project || !target) return;
  const own = target.chord_grid.map((c) => c.symbol);
  const inherited = !own.length;
  const tokens = expand(inherited ? project.chord_grid.map((c) => c.symbol) : own, target.bars);
  local = {
    sectionId,
    bar,
    tokens,
    inherited,
    diatonic: [],
    progressions: [],
    next: [],
    kind: "",
    error: "",
  };
  render();
  if (!dialog().open) dialog().showModal();
  try {
    const [diatonic, suggested] = await Promise.all([
      api.harmonyDiatonic(project.key_tonic, project.key_mode),
      api.harmonySuggest({ project_id: project.id, section_id: sectionId }),
    ]);
    if (!local || local.sectionId !== sectionId) return;
    local.diatonic = diatonic;
    local.progressions = suggested.progressions;
    local.kind = suggested.section_kind;
    render();
  } catch (e) {
    showError(e);
  }
  await loadNext();
}

/** Chord changes suggested after the chord preceding the selected bar (cyclic). */
async function loadNext() {
  const project = getState().project;
  if (!local || !project || !local.tokens.length) return;
  const n = local.tokens.length;
  const prev = local.tokens[(local.bar - 1 + n) % n];
  const at = local.bar;
  try {
    const next = await api.harmonyNext({ project_id: project.id, chord: prev });
    if (local && local.bar === at) {
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

/** Put a chord on the selected bar. @param {string} symbol */
function setBar(symbol) {
  const target = section();
  if (!local || !target) return;
  if (!local.tokens.length) local.tokens = Array(target.bars).fill(symbol);
  local.tokens[local.bar] = symbol;
  local.inherited = false;
  local.bar = Math.min(local.bar + 1, target.bars - 1);
  render();
  loadNext();
}

/** @param {number} bar */
function selectBar(bar) {
  if (!local) return;
  local.bar = bar;
  render();
  loadNext();
}

/** @param {string[]} symbols */
function useProgression(symbols) {
  if (!local) return;
  local.tokens = [...symbols];
  local.inherited = false;
  render();
  loadNext();
}

/** @param {string[] | null} grid  null = back to the project's progression */
async function save(grid) {
  if (!local) return;
  try {
    await patchSection(local.sectionId, { chord_grid: grid ?? [] });
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
    { type: "button", onclick: () => setBar(chord.symbol) },
    h("strong", null, chord.symbol),
    h("small", null, extra ? `${chord.numeral} · ${extra}` : chord.numeral),
  );
}

function render() {
  const root = body();
  const target = section();
  if (!local || !target) {
    root.replaceChildren();
    return;
  }
  const state = local;
  const bars = h("div.chord-bars", { role: "group", "aria-label": t("chords.bars") });
  const fillBars = () =>
    bars.replaceChildren(
      ...Array.from({ length: target.bars }, (_, i) =>
        h(
          `button.chord-bar${i === state.bar ? ".selected" : ""}${
            state.inherited ? ".inherited" : ""
          }`,
          { type: "button", "aria-pressed": String(i === state.bar), onclick: () => selectBar(i) },
          h("small", null, String(i + 1)),
          h("span", null, state.tokens[i] ?? "–"),
        ),
      ),
    );
  fillBars();
  // Typing only refreshes the bar strip: a full re-render would swallow the click that blurred
  // the input (e.g. on Save).
  const input = /** @type {HTMLInputElement} */ (
    h("input", {
      value: state.tokens.join(" "),
      placeholder: "Am F C G",
      "aria-label": t("chords.gridLabel"),
      onchange: () => {
        state.tokens = expand(parseChords(input.value), target.bars);
        state.inherited = false;
        fillBars();
        loadNext();
      },
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
    bars,
    h("h3", null, t("chords.next", { bar: state.bar + 1 })),
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
      "ul.progressions",
      null,
      ...state.progressions.map((p) =>
        h(
          "li",
          null,
          h(
            "button.progression",
            { type: "button", onclick: () => useProgression(p.chords.map((c) => c.symbol)) },
            h("strong", null, p.chords.map((c) => c.symbol).join(" ")),
            h("small", null, p.numerals),
          ),
        ),
      ),
    ),
    h("p.form-error", { role: "alert", hidden: !state.error }, state.error),
    h(
      "footer",
      null,
      h("button", { type: "button", onclick: () => save(null) }, t("chords.useProject")),
      h("button", { type: "button", onclick: () => dialog().close() }, t("form.close")),
      h(
        "button.primary",
        {
          type: "button",
          onclick: () => save(state.inherited ? null : parseChords(input.value)),
        },
        t("form.save"),
      ),
    ),
  );
}
