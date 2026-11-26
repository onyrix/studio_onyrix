// Header: project picker and buttons that open the (static) dialogs in index.html.

import { openProject, showError } from "../lib/actions.js";
import { h } from "../lib/dom.js";
import { t } from "../lib/i18n.js";

/** @param {string} id */
function openDialog(id) {
  const dialog = /** @type {HTMLDialogElement | null} */ (document.getElementById(id));
  dialog?.dispatchEvent(new Event("prepare"));
  dialog?.showModal();
}

/**
 * @param {HTMLElement} root
 * @param {import("../lib/store.js").State} state
 */
export function renderProjectBar(root, state) {
  root.replaceChildren();
  const select = h(
    "select",
    {
      "aria-label": t("project.label"),
      onchange: (/** @type {Event} */ e) =>
        openProject(Number(/** @type {HTMLSelectElement} */ (e.target).value)).catch(showError),
    },
    ...(state.projects.length
      ? state.projects.map((p) =>
          h("option", { value: String(p.id), selected: p.id === state.project?.id }, p.name),
        )
      : [h("option", { value: "", disabled: true, selected: true }, t("project.none"))]),
  );
  const hasProject = Boolean(state.project);
  root.append(
    select,
    h("button", { type: "button", onclick: () => openDialog("dialog-project") }, t("project.new")),
    h(
      "button",
      { type: "button", disabled: !hasProject, onclick: () => openDialog("dialog-settings") },
      t("project.settings"),
    ),
    h(
      "button",
      { type: "button", disabled: !hasProject, onclick: () => openDialog("dialog-track") },
      t("track.add"),
    ),
    h(
      "button",
      { type: "button", disabled: !hasProject, onclick: () => openDialog("dialog-section") },
      t("section.add"),
    ),
  );
}
