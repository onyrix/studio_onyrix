// Transport + export: play section / play all, loop, stop, tempo and position, zoom, export.

import { showError } from "../lib/actions.js";
import { h } from "../lib/dom.js";
import { t } from "../lib/i18n.js";
import { isPlaying, onStop, play, positionSeconds, stop } from "../lib/player.js";
import { getState, setState } from "../lib/store.js";
import { PPQ, barTicks, secondsToTicks } from "../lib/timebase.js";
import { ZOOM_LEVELS } from "./arrangement.js";

onStop(() => setState({ playing: null }));

/** @param {"section" | "all"} mode */
async function start(mode) {
  const { project, clips, selected, loop } = getState();
  if (!project) return;
  const indexes = mode === "section" ? [selected] : project.arrangement.map((_, i) => i);
  // Bars before the first played instance: where the playhead starts on the timeline.
  const bars = new Map(project.sections.map((s) => [s.id, s.bars]));
  const playFromBar = project.arrangement
    .slice(0, indexes[0] ?? 0)
    .reduce((sum, id) => sum + (bars.get(id) ?? 0), 0);
  const total = await play(project, clips, indexes, { loop });
  setState(
    total
      ? { playing: mode, playFromBar, message: "" }
      : { playing: null, message: t("transport.nothing") },
  );
}

/** @param {number} direction -1 = zoom out, +1 = zoom in */
function zoom(direction) {
  const current = ZOOM_LEVELS.indexOf(getState().zoom);
  const next = Math.min(ZOOM_LEVELS.length - 1, Math.max(0, current + direction));
  setState({ zoom: ZOOM_LEVELS[next] });
}

/** @type {HTMLElement | null} */
let positionEl = null;

/** Every frame: position text and playhead (moved with a transform, no re-render). */
function tick() {
  const { project, playing, playFromBar, zoom: pxPerBar } = getState();
  if (project) {
    const bar = barTicks(project.ts_numerator, project.ts_denominator);
    const ticks = playing && isPlaying() ? secondsToTicks(positionSeconds(), project.bpm) : 0;
    const absoluteBars = playFromBar + ticks / bar;
    if (positionEl) {
      const beatTicks = (PPQ * 4) / project.ts_denominator;
      positionEl.textContent = t("transport.position", {
        bar: Math.floor(absoluteBars) + 1,
        beat: Math.floor((ticks % bar) / beatTicks) + 1,
      });
    }
    const playhead = document.getElementById("playhead");
    if (playhead) {
      playhead.hidden = !playing;
      playhead.style.transform = `translateX(${absoluteBars * pxPerBar}px)`;
    }
  }
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);

/**
 * @param {HTMLElement} root
 * @param {import("../lib/store.js").State} state
 */
export function renderTransport(root, state) {
  const project = state.project;
  root.replaceChildren();
  if (!project) return;
  const playing = state.playing;
  positionEl = h("span.position", { "aria-live": "off" });
  root.append(
    h(
      "button.primary",
      {
        type: "button",
        "aria-pressed": String(playing === "section"),
        onclick: () => start("section").catch(showError),
      },
      "▶ ",
      t("transport.playSection"),
    ),
    h(
      "button",
      {
        type: "button",
        "aria-pressed": String(playing === "all"),
        onclick: () => start("all").catch(showError),
      },
      "▶▶ ",
      t("transport.playAll"),
    ),
    h("button", { type: "button", onclick: () => stop() }, "■ ", t("transport.stop")),
    h(
      "label.loop",
      null,
      h("input", {
        type: "checkbox",
        checked: state.loop,
        onchange: (/** @type {Event} */ e) =>
          setState({ loop: /** @type {HTMLInputElement} */ (e.target).checked }),
      }),
      t("transport.loop"),
    ),
    h("span.tempo", null, t("transport.tempo", { bpm: project.bpm })),
    positionEl,
    h(
      "span.zoom",
      { role: "group", "aria-label": t("transport.zoom") },
      h(
        "button.small",
        {
          type: "button",
          title: t("transport.zoomOut"),
          disabled: state.zoom === ZOOM_LEVELS[0],
          onclick: () => zoom(-1),
        },
        "−",
      ),
      h(
        "button.small",
        {
          type: "button",
          title: t("transport.zoomIn"),
          disabled: state.zoom === ZOOM_LEVELS[ZOOM_LEVELS.length - 1],
          onclick: () => zoom(1),
        },
        "+",
      ),
    ),
    h(
      "a.button.export",
      { href: `/api/export/project/${project.id}.mid`, download: "" },
      t("transport.exportProject"),
    ),
  );
}
