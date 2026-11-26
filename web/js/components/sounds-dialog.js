// "Suoni" dialog: installed sound banks (choose active, delete), import a downloaded bank,
// download the default bank, and licence notes for suggested downloads.

import {
  deleteSoundfont,
  downloadDefaultSoundfont,
  importSoundfont,
  setActiveSoundfont,
  showError,
} from "../lib/actions.js";
import { h } from "../lib/dom.js";
import { t } from "../lib/i18n.js";

/** @param {number} bytes */
const megabytes = (bytes) => `${(bytes / 1e6).toFixed(1)} MB`;

/**
 * @param {HTMLElement} root  the dialog body
 * @param {import("../lib/store.js").State} state
 */
export function renderSounds(root, state) {
  const info = state.soundfonts;
  const busy = Boolean(state.soundBusy);
  root.replaceChildren();
  if (!info) {
    root.append(h("p.muted", null, t("sound.loading")));
    return;
  }

  const hasDefault = info.banks.some((b) => b.id === info.default.id);
  const list = info.banks.length
    ? h(
        "ul.bank-list",
        null,
        ...info.banks.map((bank) =>
          h(
            "li",
            null,
            h(
              "label.bank-choice",
              null,
              h("input", {
                type: "radio",
                name: "active-bank",
                checked: bank.active,
                disabled: busy,
                onchange: () => setActiveSoundfont(bank.id).catch(showError),
              }),
              h("span.bank-name", null, bank.name),
              h("span.bank-meta", null, `${bank.format.toUpperCase()} · ${megabytes(bank.size)}`),
            ),
            h(
              "button.small",
              {
                type: "button",
                disabled: busy,
                title: t("sound.deleteTitle", { name: bank.name }),
                onclick: () => {
                  if (confirm(t("sound.confirmDelete", { name: bank.name }))) {
                    deleteSoundfont(bank.id).catch(showError);
                  }
                },
              },
              t("sound.delete"),
            ),
          ),
        ),
      )
    : h("p.muted", null, t("sound.none"));

  const fileInput = /** @type {HTMLInputElement} */ (
    h("input", {
      type: "file",
      accept: ".sf2,.sf3,.dls",
      disabled: busy,
      onchange: () => {
        const file = fileInput.files?.[0];
        if (file) importSoundfont(file).catch(showError);
        fileInput.value = "";
      },
    })
  );

  const parts = [
    h("h3", null, t("sound.installed")),
    list,
    state.soundBusy ? h("p.busy-line", { role: "status" }, state.soundBusy) : null,
    h("h3", null, t("sound.import")),
    h("p.muted", null, t("sound.importHint")),
    h("label.file-pick", null, fileInput),
    hasDefault
      ? null
      : h(
          "p",
          null,
          h(
            "button.primary",
            {
              type: "button",
              disabled: busy,
              onclick: () => downloadDefaultSoundfont().catch(showError),
            },
            t("sound.downloadDefault", { name: info.default.name, licence: info.default.licence }),
          ),
        ),
    h("h3", null, t("sound.suggested")),
    h(
      "ul.suggest-list",
      null,
      ...info.suggested.map((s) =>
        h(
          "li",
          null,
          h("a", { href: s.url, target: "_blank", rel: "noopener noreferrer" }, s.name),
          h("span.bank-meta", null, ` — ${s.licence} · ${t(`licenceKind.${s.licence_kind}`)}`),
        ),
      ),
    ),
    h("p.muted", null, t("sound.licenceNote")),
  ];
  // DOM append() would print null as text: keep only real nodes.
  root.append(...parts.filter((p) => p !== null));
}
