// Every user-visible string goes through this module (CLAUDE.md section 8).

/** @type {Record<string, Record<string, string>>} */
const MESSAGES = {
  it: {
    "app.title": "Studio Onyrix",
    "app.tagline": "Compositore MIDI con intelligenza artificiale",
    "status.pending": "Connessione al server…",
    "status.ok": "Server attivo (v{version})",
    "status.error": "Server non raggiungibile",

    "project.label": "Progetto",
    "project.none": "Nessun progetto",
    "project.new": "Nuovo progetto",
    "project.settings": "Impostazioni",
    "project.name": "Nome",
    "project.bpm": "BPM",
    "project.key": "Tonalità",
    "project.mode": "Modo",
    "project.genre": "Genere",
    "project.chords": "Giro di accordi",
    "project.chordsHint": "Simboli separati da spazi, es. Am F C G",
    "project.empty": "Crea un progetto per iniziare.",
    "mode.major": "maggiore",
    "mode.minor": "minore",

    "track.add": "Aggiungi traccia",
    "track.role": "Ruolo",
    "track.name": "Nome",
    "track.mute": "M",
    "track.solo": "S",
    "track.muteTitle": "Silenzia",
    "track.soloTitle": "Solo",
    "track.export": "Esporta traccia .mid",
    "role.drums": "Batteria",
    "role.bass": "Basso",
    "role.chords": "Accordi",
    "role.pad": "Pad",
    "role.lead": "Melodia",
    "role.other": "Altro",

    "section.add": "Aggiungi sezione",
    "section.defaultName": "Strofa",
    "transport.label": "Trasporto",
    "section.name": "Nome",
    "section.bars": "Battute",
    "section.chords": "Accordi (vuoto = giro del progetto)",
    "section.projectChords": "giro del progetto",
    "section.select": "Seleziona per la riproduzione",
    "section.barsCount": "{bars} battute",

    "arrangement.empty": "Aggiungi almeno una traccia e una sezione.",
    "arrangement.label": "Timeline dell'arrangiamento",
    "arrangement.tracks": "Tracce",
    "transport.zoom": "Zoom",
    "transport.zoomIn": "Ingrandisci",
    "transport.zoomOut": "Riduci",

    "cell.generate": "Genera",
    "cell.regenerate": "Rigenera",
    "cell.cancel": "Annulla",
    "cell.queued": "In coda…",
    "cell.started": "Avvio…",
    "cell.sampling": "Generazione…",
    "cell.candidate": "Candidati {count}/{total}",
    "cell.done": "Punteggio {score}",
    "cell.cancelled": "Annullato",
    "cell.error": "Errore: {message}",
    "cell.empty": "Vuoto",

    "transport.playSection": "Suona sezione",
    "transport.playAll": "Suona tutto",
    "transport.stop": "Stop",
    "transport.loop": "Loop",
    "transport.tempo": "{bpm} BPM",
    "transport.position": "Battuta {bar}.{beat}",
    "transport.exportProject": "Esporta .mid",
    "transport.nothing": "Niente da suonare",

    "form.create": "Crea",
    "form.save": "Salva",
    "form.add": "Aggiungi",
    "form.close": "Chiudi",

    "error.generic": "Errore: {message}",
  },
  en: {
    "app.title": "Studio Onyrix",
    "app.tagline": "AI MIDI composer",
    "status.pending": "Connecting to server…",
    "status.ok": "Server running (v{version})",
    "status.error": "Server unreachable",
  },
};

const NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"];

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

/** Note name for a pitch class 0..11 (music notation, not translated). @param {number} pc */
export function noteName(pc) {
  return NOTE_NAMES[((pc % 12) + 12) % 12];
}

/** Fill every element carrying `data-i18n` (text) or `data-i18n-title` (title). @param {ParentNode} root */
export function applyTranslations(root = document) {
  root.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(/** @type {string} */ (el.getAttribute("data-i18n")));
  });
  root.querySelectorAll("[data-i18n-title]").forEach((el) => {
    el.setAttribute("title", t(/** @type {string} */ (el.getAttribute("data-i18n-title"))));
  });
}
