// Arrangement view: rows = section instances in order, columns = tracks.

import { cancel, generate, patchTrack, showError } from "../lib/actions.js";
import { drawClip } from "../components/clip-preview.js";
import { h } from "../lib/dom.js";
import { noteName, t } from "../lib/i18n.js";
import { jobKey, setState } from "../lib/store.js";
import { barTicks } from "../lib/timebase.js";

const ACTIVE = new Set(["queued", "started", "sampling", "candidate"]);

/** @param {Array<{root: number, quality: string}>} grid */
function chordText(grid) {
  return grid.length ? grid.map((c) => noteName(c.root) + c.quality).join(" ") : "";
}

/** @param {import("../lib/store.js").JobState | undefined} job */
function jobText(job) {
  if (!job) return "";
  const d = job.detail ?? {};
  switch (job.status) {
    case "candidate":
      return t("cell.candidate", { count: d.count ?? 0, total: d.total ?? "?" });
    case "done":
      return t("cell.done", { score: Number(d.score ?? 0).toFixed(2) });
    case "error":
      return t("cell.error", { message: d.message ?? "" });
    default:
      return t(`cell.${job.status}`);
  }
}

/** @param {import("../lib/store.js").Track} track */
function trackHeader(track) {
  const toggle = (/** @type {"mute"|"solo"} */ field) =>
    h(
      `button.toggle.${field}`,
      {
        type: "button",
        title: t(`track.${field}Title`),
        "aria-pressed": String(track[field]),
        onclick: () => patchTrack(track.id, { [field]: !track[field] }).catch(showError),
      },
      t(`track.${field}`),
    );
  return h(
    "div.track-head",
    null,
    h("div.track-name", null, track.name),
    h("div.track-role", null, t(`role.${track.role}`)),
    h(
      "div.track-actions",
      null,
      toggle("mute"),
      toggle("solo"),
      h("a.export-link", { href: `/api/export/track/${track.id}.mid`, title: t("track.export") }, "MIDI"),
    ),
  );
}

/**
 * @param {HTMLElement} root
 * @param {import("../lib/store.js").State} state
 */
export function renderArrangement(root, state) {
  const project = state.project;
  root.replaceChildren();
  if (!project) {
    root.append(h("p.empty", null, t("project.empty")));
    return;
  }
  const tracks = [...project.tracks].sort((a, b) => a.position - b.position);
  if (!tracks.length || !project.arrangement.length) {
    root.append(h("p.empty", null, t("arrangement.empty")));
  }
  if (!tracks.length && !project.arrangement.length) return;

  const sections = new Map(project.sections.map((s) => [s.id, s]));
  const bar = barTicks(project.ts_numerator, project.ts_denominator);
  const grid = h("div.grid", { role: "grid" });
  grid.style.setProperty("--tracks", String(tracks.length));

  grid.append(h("div.corner"), ...tracks.map(trackHeader));

  /** @type {Array<() => void>} */
  const draws = [];
  project.arrangement.forEach((sectionId, index) => {
    const section = sections.get(sectionId);
    if (!section) return;
    const selected = index === state.selected;
    grid.append(
      h(
        `button.section-head${selected ? ".selected" : ""}`,
        {
          type: "button",
          title: t("section.select"),
          "aria-pressed": String(selected),
          onclick: () => setState({ selected: index }),
        },
        h("span.section-name", null, section.name),
        h("span.section-meta", null, t("section.barsCount", { bars: section.bars })),
        h(
          "span.section-chords",
          null,
          chordText(section.chord_grid) || `(${t("section.projectChords")})`,
        ),
      ),
    );

    for (const track of tracks) {
      const clipId = section.slots[String(track.id)];
      const clip = clipId ? state.clips[clipId] : undefined;
      const notes = clip?.current_version?.notes ?? [];
      const job = state.jobs[jobKey(section.id, track.id)];
      const busy = job ? ACTIVE.has(job.status) : false;
      const canvas = /** @type {HTMLCanvasElement} */ (h("canvas.clip-canvas", { "aria-hidden": "true" }));
      draws.push(() => drawClip(canvas, notes, section.bars * bar, bar, track.role === "drums"));

      const action = busy
        ? h(
            "button.secondary",
            { type: "button", onclick: () => cancel(section.id, track.id).catch(showError) },
            t("cell.cancel"),
          )
        : h(
            "button.primary",
            { type: "button", onclick: () => generate(section.id, track.id).catch(showError) },
            clip ? t("cell.regenerate") : t("cell.generate"),
          );
      grid.append(
        h(
          `div.cell${busy ? ".busy" : ""}${selected ? ".selected" : ""}${track.mute ? ".muted" : ""}`,
          { role: "gridcell" },
          canvas,
          h(
            "div.cell-foot",
            null,
            h("span.cell-status", { "aria-live": "polite" }, jobText(job) || (clip ? "" : t("cell.empty"))),
            action,
          ),
        ),
      );
    }
  });
  root.append(grid);
  requestAnimationFrame(() => draws.forEach((draw) => draw()));
}
