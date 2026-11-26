// Arrangement view: a left-to-right timeline.
// Rows = tracks; section instances = blocks of bars (width proportional to their length);
// each block on a track row is that track's part (clip) in that section instance.

import { cancel, generate, patchTrack, showError } from "../lib/actions.js";
import { openChordDialog } from "../components/chord-dialog.js";
import { drawClip } from "../components/clip-preview.js";
import { h } from "../lib/dom.js";
import { t } from "../lib/i18n.js";
import { jobKey, setState } from "../lib/store.js";
import { barTicks } from "../lib/timebase.js";

const ACTIVE = new Set(["queued", "started", "sampling", "candidate"]);
export const ZOOM_LEVELS = [24, 36, 56, 80, 120];

/** @param {Array<{symbol: string}>} grid */
function chordText(grid) {
  return grid.map((c) => c.symbol).join(" ");
}

/**
 * Chord lane block for one section instance: one button per bar, the section's own grid or
 * (faded) the project's progression cycled over the section, as the generator does.
 * @param {import("../lib/store.js").Section} section
 * @param {import("../lib/store.js").Chord[]} projectGrid
 * @param {boolean} selected
 * @param {number} zoom  px per bar
 */
function chordBlock(section, projectGrid, selected, zoom) {
  const inherited = !section.chord_grid.length;
  const grid = inherited ? projectGrid : section.chord_grid;
  const block = h(
    `div.tl-chord-block${inherited ? ".inherited" : ""}${selected ? ".selected" : ""}`,
  );
  for (let bar = 0; bar < section.bars; bar++) {
    const symbol = grid.length ? grid[bar % grid.length].symbol : "";
    const repeated = bar > 0 && grid.length > 0 && grid[(bar - 1) % grid.length].symbol === symbol;
    block.append(
      h(
        "button.tl-chord",
        {
          type: "button",
          title: t("chords.edit", { section: section.name, bar: bar + 1 }),
          onclick: () => openChordDialog(section.id, bar).catch(showError),
        },
        repeated ? "%" : symbol || "–",
      ),
    );
  }
  block.style.width = `${section.bars * zoom}px`;
  return block;
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
function trackHead(track) {
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
    "div.tl-head",
    { role: "rowheader" },
    h(
      "div.tl-head-text",
      null,
      h("div.track-name", null, track.name),
      h("div.track-role", null, t(`role.${track.role}`)),
    ),
    h(
      "div.track-actions",
      null,
      toggle("mute"),
      toggle("solo"),
      h("a.export-link", { href: `/api/export/track/${track.id}.mid`, title: t("track.export") }, "MIDI"),
    ),
  );
}

/** Keep the horizontal scroll position across re-renders. */
let scrollLeft = 0;

/**
 * @param {HTMLElement} root
 * @param {import("../lib/store.js").State} state
 */
export function renderArrangement(root, state) {
  const previous = root.querySelector(".timeline");
  if (previous) scrollLeft = previous.scrollLeft;
  root.replaceChildren();

  const project = state.project;
  if (!project) {
    root.append(h("p.empty", null, t("project.empty")));
    return;
  }
  const tracks = [...project.tracks].sort((a, b) => a.position - b.position);
  if (!tracks.length || !project.arrangement.length) {
    root.append(h("p.empty", null, t("arrangement.empty")));
    if (!tracks.length && !project.arrangement.length) return;
  }

  const sections = new Map(project.sections.map((s) => [s.id, s]));
  const barLength = barTicks(project.ts_numerator, project.ts_denominator);
  const zoom = state.zoom;
  const instances = project.arrangement
    .map((id, index) => ({ index, section: sections.get(id) }))
    .filter((i) => i.section !== undefined);
  const totalBars = instances.reduce((sum, i) => sum + (i.section?.bars ?? 0), 0);

  const grid = h("div.tl-grid", { role: "grid", "aria-label": t("arrangement.label") });
  grid.style.setProperty("--zoom", `${zoom}px`);
  grid.style.setProperty("--lanes-width", `${Math.max(totalBars, 1) * zoom}px`);

  // Header row: section blocks with bar numbers.
  let firstBar = 1;
  const ruler = h("div.tl-ruler", { role: "row" });
  for (const { index, section } of instances) {
    if (!section) continue;
    const selected = index === state.selected;
    const chords = chordText(section.chord_grid);
    const numbers = h(
      "div.bar-numbers",
      { "aria-hidden": "true" },
      ...Array.from({ length: section.bars }, (_, b) => h("span", null, String(firstBar + b))),
    );
    const block = h(
      `button.tl-section${selected ? ".selected" : ""}`,
      {
        type: "button",
        title: `${section.name} · ${t("section.barsCount", { bars: section.bars })} · ${
          chords || t("section.projectChords")
        }`,
        "aria-pressed": String(selected),
        onclick: () => setState({ selected: index }),
      },
      h(
        "span.tl-section-label",
        null,
        h("span.section-name", null, section.name),
        h("span.section-chords", null, chords),
      ),
      numbers,
    );
    block.style.width = `${section.bars * zoom}px`;
    ruler.append(block);
    firstBar += section.bars;
  }
  grid.append(h("div.tl-corner", null, t("arrangement.tracks")), ruler);

  // Chord lane: one chord per bar, click to edit the section's grid.
  const chordLane = h("div.tl-chords", { role: "row" });
  for (const { index, section } of instances) {
    if (section) {
      chordLane.append(chordBlock(section, project.chord_grid, index === state.selected, zoom));
    }
  }
  grid.append(h("div.tl-corner.tl-chords-head", null, t("chords.lane")), chordLane);

  // One row per track: a part (clip) block per section instance.
  /** @type {Array<() => void>} */
  const draws = [];
  for (const track of tracks) {
    const lane = h(`div.tl-lane${track.mute ? ".muted" : ""}`, { role: "row" });
    for (const { index, section } of instances) {
      if (!section) continue;
      const clipId = section.slots[String(track.id)];
      const clip = clipId ? state.clips[clipId] : undefined;
      const notes = clip?.current_version?.notes ?? [];
      const job = state.jobs[jobKey(section.id, track.id)];
      const busy = job ? ACTIVE.has(job.status) : false;
      const canvas = /** @type {HTMLCanvasElement} */ (
        h("canvas.clip-canvas", { "aria-hidden": "true" })
      );
      draws.push(() =>
        drawClip(canvas, notes, section.bars * barLength, barLength, track.role === "drums"),
      );
      const action = busy
        ? h(
            "button.small.secondary",
            { type: "button", onclick: () => cancel(section.id, track.id).catch(showError) },
            t("cell.cancel"),
          )
        : h(
            `button.small${clip ? "" : ".primary"}`,
            {
              type: "button",
              title: `${clip ? t("cell.regenerate") : t("cell.generate")}: ${track.name} · ${section.name}`,
              onclick: () => generate(section.id, track.id).catch(showError),
            },
            clip ? t("cell.regenerate") : t("cell.generate"),
          );
      const part = h(
        `div.tl-part${clip ? ".filled" : ".empty-part"}${busy ? ".busy" : ""}${
          index === state.selected ? ".selected" : ""
        }`,
        { role: "gridcell" },
        canvas,
        h(
          "div.tl-part-overlay",
          null,
          h("span.cell-status", { "aria-live": "polite" }, jobText(job)),
          action,
        ),
      );
      part.style.width = `${section.bars * zoom}px`;
      lane.append(part);
    }
    grid.append(trackHead(track), lane);
  }

  grid.append(h("div.playhead", { id: "playhead", "aria-hidden": "true" }));
  const timeline = h("div.timeline", null, grid);
  root.append(timeline);
  timeline.scrollLeft = scrollLeft;
  requestAnimationFrame(() => draws.forEach((draw) => draw()));
}
