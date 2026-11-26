// Every user-visible string goes through this module (CLAUDE.md section 8).

/** @type {Record<string, Record<string, string>>} */
const MESSAGES = {
  it: {
    "app.title": "Studio Onyrix",
    "app.tagline": "Compositore MIDI con intelligenza artificiale",
    "status.pending": "Connessione al server…",
    "status.ok": "Server attivo (v{version})",
    "status.error": "Server non raggiungibile",
  },
  en: {
    "app.title": "Studio Onyrix",
    "app.tagline": "AI MIDI composer",
    "status.pending": "Connecting to server…",
    "status.ok": "Server running (v{version})",
    "status.error": "Server unreachable",
  },
};

let locale = "it";

/** @param {string} next */
export function setLocale(next) {
  if (next in MESSAGES) locale = next;
}

/**
 * @param {string} key
 * @param {Record<string, string | number>} [params]
 * @returns {string}
 */
export function t(key, params = {}) {
  const template = MESSAGES[locale][key] ?? MESSAGES.it[key] ?? key;
  return template.replace(/\{(\w+)\}/g, (_, name) => String(params[name] ?? `{${name}}`));
}

/** Fill every element carrying a `data-i18n` attribute. @param {ParentNode} root */
export function applyTranslations(root = document) {
  root.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(/** @type {string} */ (el.getAttribute("data-i18n")));
  });
}
