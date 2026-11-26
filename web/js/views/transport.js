// Transport + export: play section / play all, loop, stop, tempo and position, zoom, export.

import { showError } from "../lib/actions.js";
import { h } from "../lib/dom.js";
import { t } from "../lib/i18n.js";
import { applyMutes, isPlaying, onStop, play, positionSeconds, stop } from "../lib/player.js";
import { getState, setState } from "../lib/store.js";
import { PPQ, barTicks, secondsToTicks } from "../lib/timebase.js";
import { ZOOM_LEVELS } from "./arrangement.js";

onStop(() => setState({ playing: null }));

/** @param {string} id */
function openDialog(id) {
  const dialog = /** @type {HTMLDialogElement | null} */ (document.getElementById(id));
  dialog?.dispatchEvent(new Event("prepare"));
  dialog?.showModal();
}

/** True if any part in the given instances has notes. @param {number[]} indexes */
function hasNotes(indexes) {
  const { project, clips } = getState();
  if (!project) return false;
  const sections = new Map(project.sections.map((s) => [s.id, s]));
  return indexes.some((i) => {
    const section = sections.get(project.arrangement[i]);
    return Object.values(section?.slots ?? {}).some(
      (clipId) => (clips[clipId]?.current_version?.notes ?? []).length > 0,
    );
  });
}

/** @param {"section" | "all"} mode */
async function start(mode) {
  const { project, selected, loop, soundfonts } = getState();
  if (!project || !project.arrangement.length) return;
  const indexes = mode === "section" ? [selected] : project.arrangement.map((_, i) => i);
  if (!hasNotes(indexes)) {
    setState({ message: t("transport.nothing") });
    return;
  }
  const bankId = soundfonts?.active;
  if (!bankId) {
    setState({ message: t("sound.needBank") });
    openDialog("dialog-sounds");
    return;
  }
  // Bars before the first played instance: where the playhead starts on the timeline.
  const bars = new Map(project.sections.map((s) => [s.id, s.bars]));
  const playFromBar = project.arrangement
    .slice(0, indexes[0])
    .reduce((sum, id) => sum + (bars.get(id) ?? 0), 0);
  setState({ message: t("sound.preparing") });
  await play(project, indexes, { loop, bankId });
  setState({ playing: mode, playFromBar, message: "" });
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
  if (isPlaying()) applyMutes([...project.tracks].sort((a, b) => a.position - b.position));
  const playing = state.playing;
  const bank = state.soundfonts?.banks.find((b) => b.active);
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
      "button.sound-button",
      { type: "button", title: t("sound.title"), onclick: () => openDialog("dialog-sounds") },
      "♫ ",
      bank ? bank.name : t("sound.noneShort"),
    ),
    h(
      "a.button.export",
      { href: `/api/export/project/${project.id}.mid`, download: "" },
      t("transport.exportProject"),
    ),
  );
}
