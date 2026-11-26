// Transport + export: play section / play all, loop, stop, tempo and position, export.

import { showError } from "../lib/actions.js";
import { h } from "../lib/dom.js";
import { t } from "../lib/i18n.js";
import { isPlaying, onStop, play, positionSeconds, stop } from "../lib/player.js";
import { getState, setState } from "../lib/store.js";
import { secondsToTicks, barTicks, PPQ } from "../lib/timebase.js";

onStop(() => setState({ playing: null }));

/** @param {"section" | "all"} mode */
async function start(mode) {
  const { project, clips, selected, loop } = getState();
  if (!project) return;
  const indexes = mode === "section" ? [selected] : project.arrangement.map((_, i) => i);
  const total = await play(project, clips, indexes, { loop });
  setState(total ? { playing: mode, message: "" } : { playing: null, message: t("transport.nothing") });
}

/** @type {HTMLElement | null} */
let positionEl = null;

function tick() {
  const project = getState().project;
  if (positionEl && project) {
    const ticks = isPlaying() ? secondsToTicks(positionSeconds(), project.bpm) : 0;
    const bar = barTicks(project.ts_numerator, project.ts_denominator);
    const beatTicks = (PPQ * 4) / project.ts_denominator;
    positionEl.textContent = t("transport.position", {
      bar: Math.floor(ticks / bar) + 1,
      beat: Math.floor((ticks % bar) / beatTicks) + 1,
    });
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
      "a.button.export",
      { href: `/api/export/project/${project.id}.mid`, download: "" },
      t("transport.exportProject"),
    ),
  );
}
