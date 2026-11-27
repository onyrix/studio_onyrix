// Harmonic explorer panel inside the chord dialog (B-57 / B-58): how surprising the current
// progression is, operators that transform it (on the selected chord or on all of it), a
// generator with an "audacity" control, and the optional chord corpus that feeds the statistics.
// All the music logic lives on the server (core/operators.py, core/harmony_stats.py).

import { audition, showError } from "../lib/actions.js";
import { api } from "../lib/api.js";
import { h } from "../lib/dom.js";
import { t } from "../lib/i18n.js";
import { getState } from "../lib/store.js";

/**
 * @typedef {{symbol: string, beats: number}} Event
 * @typedef {{chords: Array<{symbol: string, beats: number}>, chord_text: string, numerals: string, surprise: number, surprise_level: number}} Described
 * @typedef {{
 *   text: string, selected: number, selectedSymbol: string, sectionId: number,
 *   apply: (events: Event[]) => void, onError: (message: string) => void,
 * }} Context
 */

const state = {
  /** @type {Array<{id: string, scope: string}>} */
  operators: [],
  /** @type {Described[]} */
  ideas: [],
  audacity: 0.3,
  length: 4,
  seed: 1,
  /** @type {{numerals: string, surprise_level: number} | null} */
  info: null,
  /** @type {any} */
  corpus: null,
  busy: false,
  infoFor: "",
};

/** @type {() => void} */
let rerender = () => {};
/** @type {ReturnType<typeof setTimeout> | null} */
let poll = null;

/** @param {() => void} fn  re-render the dialog */
export function initExplorer(fn) {
  rerender = fn;
}

export async function loadExplorer() {
  try {
    const [operators, corpus] = await Promise.all([api.harmonyOperators(), api.corpus()]);
    state.operators = operators;
    state.corpus = corpus;
    state.ideas = [];
    rerender();
    watchCorpus();
  } catch (e) {
    showError(e);
  }
}

/** Numerals and surprise of the current progression (cached per text). @param {string} text @param {number} sectionId */
export async function refreshInfo(text, sectionId) {
  const project = getState().project;
  if (!project || !text.trim() || text === state.infoFor) return;
  state.infoFor = text;
  try {
    const parsed = await api.harmonyParse({ project_id: project.id, text, section_id: sectionId });
    if (state.infoFor !== text) return;
    state.info = { numerals: parsed.numerals, surprise_level: parsed.surprise_level };
    rerender();
  } catch {
    state.info = null;
    rerender();
  }
}

function watchCorpus() {
  if (poll) clearTimeout(poll);
  const busy = ["downloading", "building"].includes(state.corpus?.state);
  if (!busy) return;
  poll = setTimeout(async () => {
    try {
      state.corpus = await api.corpus();
      if (state.corpus.state === "ready") state.infoFor = ""; // statistics changed
      rerender();
    } catch {
      /* keep polling */
    }
    watchCorpus();
  }, 1000);
}

async function startCorpus() {
  if (!window.confirm(t("corpus.confirm", { size: Math.round((state.corpus?.corpus?.size ?? 0) / 1e6) }))) return;
  try {
    state.corpus = await api.corpusDownload();
    rerender();
    watchCorpus();
  } catch (e) {
    showError(e);
  }
}

async function deleteCorpus() {
  if (!window.confirm(t("corpus.confirmDelete"))) return;
  try {
    await api.corpusDelete();
    state.corpus = await api.corpus();
    state.infoFor = "";
    rerender();
  } catch (e) {
    showError(e);
  }
}

/** @param {Context} ctx @param {string} operator */
async function applyOperator(ctx, operator) {
  const project = getState().project;
  if (!project || !ctx.text.trim()) return;
  try {
    const out = await api.harmonyTransform({
      project_id: project.id,
      section_id: ctx.sectionId,
      text: ctx.text,
      operator,
      index: ctx.selected,
    });
    ctx.apply(out.chords.map((/** @type {any} */ c) => ({ symbol: c.symbol, beats: c.beats })));
  } catch (e) {
    const detail = e instanceof Error ? e.message : String(e);
    ctx.onError(t("explore.notApplicable", { op: t(`op.${operator}`), detail }));
  }
}

/** @param {Context} ctx */
async function generate(ctx) {
  const project = getState().project;
  if (!project) return;
  state.busy = true;
  rerender();
  try {
    const out = await api.harmonyExplore({
      project_id: project.id,
      section_id: ctx.sectionId,
      length: state.length,
      audacity: state.audacity,
      seed: state.seed,
      n: 6,
    });
    state.ideas = out.progressions;
    state.seed += 1;
  } catch (e) {
    showError(e);
  } finally {
    state.busy = false;
    rerender();
  }
}

/** Surprise meter. @param {number} level 0..1 */
export function meter(level) {
  const label = level < 0.25 ? "common" : level < 0.5 ? "personal" : level < 0.75 ? "bold" : "wild";
  const bar = h("span.meter-fill");
  bar.style.width = `${Math.round(Math.max(0.04, level) * 100)}%`;
  return h(
    "span.meter",
    { title: t("explore.surpriseTitle"), role: "img", "aria-label": t(`explore.level.${label}`) },
    h("span.meter-track", null, bar),
    h("small", null, t(`explore.level.${label}`)),
  );
}

function corpusLine() {
  const c = state.corpus;
  if (!c) return null;
  const info = c.corpus;
  const source = c.source === "chordonomicon" ? t("corpus.sourceCorpus") : t("corpus.sourceLibrary");
  /** @type {Array<Node | string | null>} */
  const parts = [h("span", null, t("corpus.statsFrom", { source }))];
  if (c.state === "missing" || c.state === "error") {
    parts.push(
      h(
        "button.small",
        { type: "button", onclick: () => startCorpus() },
        t("corpus.download", { name: info.name, size: Math.round(info.size / 1e6) }),
      ),
    );
  }
  if (c.state === "downloading" || c.state === "building") {
    parts.push(h("span", null, t(`corpus.${c.state}`, { percent: Math.round(c.progress * 100) })));
  }
  if (c.state === "ready") {
    parts.push(h("button.small", { type: "button", onclick: () => deleteCorpus() }, t("corpus.delete")));
  }
  if (c.state === "error") parts.push(h("span.form-error", null, t("corpus.error", { message: c.error ?? "" })));
  return h(
    "div.corpus-line",
    null,
    ...parts,
    h(
      "small.muted",
      null,
      `${info.name}: ${info.licence}, `,
      h("a", { href: info.homepage, target: "_blank", rel: "noopener" }, t("corpus.source")),
      ` — ${info.attribution}`,
    ),
  );
}

/** @param {Context} ctx */
export function explorerPanel(ctx) {
  const byScope = (/** @type {string} */ scope) =>
    state.operators
      .filter((op) => op.scope === scope)
      .map((op) =>
        h(
          "button.small",
          { type: "button", title: t(`op.${op.id}.help`), onclick: () => applyOperator(ctx, op.id) },
          t(`op.${op.id}`),
        ),
      );
  const slider = /** @type {HTMLInputElement} */ (
    h("input", {
      type: "range",
      min: "0",
      max: "100",
      value: String(Math.round(state.audacity * 100)),
      "aria-label": t("explore.audacity"),
      oninput: () => {
        state.audacity = Number(slider.value) / 100;
      },
    })
  );
  const length = /** @type {HTMLSelectElement} */ (
    h(
      "select",
      { "aria-label": t("explore.length"), onchange: () => (state.length = Number(length.value)) },
      ...[3, 4, 6, 8].map((n) => h("option", { value: String(n), selected: n === state.length }, t("explore.chords", { n }))),
    )
  );
  return h(
    "details.explorer",
    { open: true },
    h("summary", null, t("explore.title")),
    state.info
      ? h("p.current-info", null, h("span", null, `${state.info.numerals} `), meter(state.info.surprise_level))
      : null,
    h("h4", null, t("explore.onChord", { chord: ctx.selectedSymbol || "–" })),
    h("div.chips", null, ...byScope("chord")),
    h("h4", null, t("explore.onProgression")),
    h("div.chips", null, ...byScope("progression")),
    h("h4", null, t("explore.generate")),
    h(
      "div.explore-controls",
      null,
      h("label.inline", null, h("span", null, t("explore.idiomatic")), slider, h("span", null, t("explore.bold"))),
      length,
      h(
        "button.small.primary",
        { type: "button", disabled: state.busy, onclick: () => generate(ctx) },
        state.busy ? t("explore.generating") : t("explore.generateButton"),
      ),
    ),
    state.ideas.length
      ? h(
          "ul.progressions",
          null,
          ...state.ideas.map((idea) =>
            h(
              "li.progression-row",
              null,
              h(
                "button.small.listen",
                { type: "button", "aria-label": t("chords.listen"), onclick: () => audition(idea.chord_text).catch(showError) },
                "▶",
              ),
              h(
                "button.progression",
                {
                  type: "button",
                  title: t("chords.use"),
                  onclick: () => ctx.apply(idea.chords.map((c) => ({ symbol: c.symbol, beats: c.beats }))),
                },
                h("strong", null, idea.chord_text),
                h("small", null, idea.numerals, " ", meter(idea.surprise_level)),
              ),
            ),
          ),
        )
      : null,
    corpusLine(),
  );
}
