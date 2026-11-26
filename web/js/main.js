import {
  addSection,
  addTrack,
  createProject,
  loadProjects,
  loadSoundfonts,
  openProject,
  parseChords,
  showError,
  updateProject,
} from "./lib/actions.js";
import { api } from "./lib/api.js";
import { h } from "./lib/dom.js";
import { applyTranslations, noteName, t } from "./lib/i18n.js";
import { getState, setState, subscribe } from "./lib/store.js";
import { renderProjectBar } from "./components/project-bar.js";
import { renderSounds } from "./components/sounds-dialog.js";
import { renderArrangement } from "./views/arrangement.js";
import { renderTransport } from "./views/transport.js";

const $ = (/** @type {string} */ id) => /** @type {HTMLElement} */ (document.getElementById(id));

const ROLES = ["drums", "bass", "chords", "pad", "lead", "other"];

/** Populate <select data-options="..."> lists. */
function fillOptions() {
  /** @type {Record<string, Array<[string, string]>>} */
  const lists = {
    keys: Array.from({ length: 12 }, (_, pc) => [String(pc), noteName(pc)]),
    modes: [
      ["major", t("mode.major")],
      ["minor", t("mode.minor")],
    ],
    roles: ROLES.map((r) => [r, t(`role.${r}`)]),
  };
  document.querySelectorAll("select[data-options]").forEach((select) => {
    const items = lists[/** @type {string} */ (select.getAttribute("data-options"))] ?? [];
    select.replaceChildren(...items.map(([value, label]) => h("option", { value }, label)));
  });
}

/** @param {Array<{symbol: string}>} grid */
const chordsToText = (grid) => grid.map((c) => c.symbol).join(" ");

/** @param {HTMLFormElement} form */
function formValues(form) {
  return Object.fromEntries(new FormData(form).entries());
}

/** @type {Record<string, (v: Record<string, any>) => Promise<void>>} */
const SUBMIT = {
  "create-project": (v) =>
    createProject({
      name: v.name,
      bpm: Number(v.bpm),
      key_tonic: Number(v.key_tonic),
      key_mode: v.key_mode,
      genre: v.genre,
      chord_grid: parseChords(v.chords),
    }),
  "update-project": (v) =>
    updateProject({
      name: v.name,
      bpm: Number(v.bpm),
      key_tonic: Number(v.key_tonic),
      key_mode: v.key_mode,
      genre: v.genre,
      chord_grid: parseChords(v.chords),
    }),
  "add-track": (v) => addTrack({ role: v.role, name: v.name || undefined }),
  "add-section": (v) =>
    addSection({ name: v.name, bars: Number(v.bars), chord_grid: parseChords(v.chords) }),
};

function wireDialogs() {
  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.querySelectorAll("[data-close]").forEach((b) =>
      b.addEventListener("click", () => dialog.close()),
    );
    const maybeForm = dialog.querySelector("form");
    if (!maybeForm) return;
    const form = /** @type {HTMLFormElement} */ (maybeForm);
    const error = h("p.form-error", { role: "alert", hidden: true });
    form.querySelector("footer")?.before(error);
    dialog.addEventListener("prepare", () => {
      form.reset();
      error.hidden = true;
      const project = getState().project;
      const field = (/** @type {string} */ name) =>
        /** @type {HTMLInputElement} */ (form.elements.namedItem(name));
      if (dialog.id === "dialog-settings" && project) {
        field("name").value = project.name;
        field("bpm").value = String(project.bpm);
        field("key_tonic").value = String(project.key_tonic);
        field("key_mode").value = project.key_mode;
        field("genre").value = project.genre;
        field("chords").value = chordsToText(project.chord_grid);
      }
      if (dialog.id === "dialog-section") field("name").value = t("section.defaultName");
    });
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const action = SUBMIT[/** @type {string} */ (form.dataset.action)];
      try {
        await action(formValues(form));
        dialog.close();
      } catch (e) {
        error.textContent = e instanceof Error ? e.message : String(e);
        error.hidden = false;
      }
    });
  });
}

function render() {
  const state = getState();
  renderProjectBar($("project-bar"), state);
  renderTransport($("transport"), state);
  renderArrangement($("arrangement"), state);
  renderSounds($("sounds-body"), state);
  const message = $("message");
  message.textContent = state.message;
  message.hidden = !state.message;
}

async function checkHealth() {
  const status = $("status");
  try {
    const health = await api.health();
    status.textContent = t("status.ok", { version: health.version });
    status.dataset.state = "ok";
  } catch {
    status.textContent = t("status.error");
    status.dataset.state = "error";
  }
}

async function init() {
  applyTranslations();
  $("transport").setAttribute("aria-label", t("transport.label"));
  $("status").textContent = t("status.pending");
  $("message").addEventListener("click", () => setState({ message: "" }));
  fillOptions();
  wireDialogs();
  subscribe(render);
  render();
  await checkHealth();
  await Promise.all([loadProjects(), loadSoundfonts()]);
  const first = getState().projects[0];
  if (first) await openProject(first.id);
  else {
    const dialog = /** @type {HTMLDialogElement} */ ($("dialog-project"));
    dialog.dispatchEvent(new Event("prepare"));
    dialog.showModal();
  }
}

init().catch(showError);
