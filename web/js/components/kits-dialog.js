// Song kits dialog: whole-song chord plans (intro / verse / pre-chorus / chorus / bridge / outro
// designed to belong together), in the project key, filterable by mood, each part audible.
// Applying a kit writes its parts into the sections of matching kind and creates the missing
// ones (an empty song gets a complete form).

import { applyKit, audition, showError } from "../lib/actions.js";
import { api } from "../lib/api.js";
import { h } from "../lib/dom.js";
import { t } from "../lib/i18n.js";
import { getState } from "../lib/store.js";
import { MOODS } from "./chord-dialog.js";

/**
 * @typedef {{kind: string, chord_text: string, numerals: string, bars: number}} KitPart
 * @typedef {{id: string, moods: string[], genres: string[], parts: KitPart[]}} Kit
 * @typedef {{moods: string[], kits: Kit[], busy: string, error: string}} Local
 */

/** @type {Local} */
const local = { moods: [], kits: [], busy: "", error: "" };

const dialog = () => /** @type {HTMLDialogElement} */ (document.getElementById("dialog-kits"));
const body = () => /** @type {HTMLElement} */ (document.getElementById("kits-body"));

/** @param {string} text */
const capitalize = (text) => text.charAt(0).toUpperCase() + text.slice(1);

export async function openKitsDialog() {
  local.error = "";
  render();
  if (!dialog().open) dialog().showModal();
  await load();
}

async function load() {
  const project = getState().project;
  if (!project) return;
  const moods = local.moods;
  try {
    const kits = await api.kits(project.id, moods);
    if (local.moods !== moods) return;
    local.kits = kits;
  } catch (e) {
    local.error = e instanceof Error ? e.message : String(e);
  }
  render();
}

/** @param {string} mood */
function toggleMood(mood) {
  local.moods = local.moods.includes(mood)
    ? local.moods.filter((m) => m !== mood)
    : [...local.moods, mood];
  render();
  load();
}

/** @param {Kit} kit */
async function apply(kit) {
  /** @type {Record<string, string>} */
  const names = {};
  for (const part of kit.parts) names[part.kind] = capitalize(t(`sectionKind.${part.kind}`));
  local.busy = kit.id;
  render();
  try {
    await applyKit(kit.id, names);
    dialog().close();
  } catch (e) {
    local.error = e instanceof Error ? e.message : String(e);
  } finally {
    local.busy = "";
    render();
  }
}

/** @param {Kit} kit */
function kitCard(kit) {
  return h(
    "li.kit",
    null,
    h(
      "div.kit-head",
      null,
      h("strong", null, t(`kit.${kit.id}`)),
      h("small", null, kit.moods.map((m) => t(`mood.${m}`)).join(", ")),
      h(
        "button.small.primary",
        { type: "button", disabled: Boolean(local.busy), onclick: () => apply(kit) },
        local.busy === kit.id ? t("kits.applying") : t("kits.apply"),
      ),
    ),
    h(
      "table.kit-parts",
      null,
      h(
        "tbody",
        null,
        ...kit.parts.map((part) =>
          h(
            "tr",
            null,
            h(
              "td",
              null,
              h(
                "button.small.listen",
                {
                  type: "button",
                  title: t("chords.listen"),
                  "aria-label": `${t("chords.listen")}: ${t(`sectionKind.${part.kind}`)}`,
                  onclick: () => audition(part.chord_text).catch(showError),
                },
                "▶",
              ),
            ),
            h("th", { scope: "row" }, capitalize(t(`sectionKind.${part.kind}`))),
            h("td", null, h("strong", null, part.chord_text), h("small", null, part.numerals)),
          ),
        ),
      ),
    ),
  );
}

function render() {
  const project = getState().project;
  body().replaceChildren(
    h("h2", null, t("kits.title")),
    h("p.muted", null, t("kits.hint")),
    h(
      "div.chips.moods",
      { role: "group", "aria-label": t("chords.moods") },
      ...MOODS.map((mood) =>
        h(
          `button.small.mood${local.moods.includes(mood) ? ".primary" : ""}`,
          {
            type: "button",
            "aria-pressed": String(local.moods.includes(mood)),
            onclick: () => toggleMood(mood),
          },
          t(`mood.${mood}`),
        ),
      ),
    ),
    project && local.kits.length
      ? h("ul.kits", null, ...local.kits.map(kitCard))
      : h("p.muted", null, t("chords.noMatch")),
    h("p.form-error", { role: "alert", hidden: !local.error }, local.error),
    h(
      "footer",
      null,
      h("button", { type: "button", onclick: () => dialog().close() }, t("form.close")),
    ),
  );
}
