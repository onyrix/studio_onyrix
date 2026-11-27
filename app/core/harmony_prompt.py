"""From a free-text request ("malinconico ma che si apre, tipo pop, con settime") to harmonic
parameters for the explorer (B-59). Pure.

`HarmonyIntent` is the structured form: moods, mode, genre, section kind, audacity, length and
progression operators. `KeywordHarmonyInterpreter` reads Italian and English keywords offline;
an LLM (local Ollama, `app.gen.prompting`) can produce the same structure, and its answer always
goes through `validate_intent`, which drops anything unknown and clamps numbers: the LLM
proposes, the rules decide.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from app.core.library import MOODS, PART_ORDER
from app.core.model import Mode

GENRES = (
    "pop",
    "rock",
    "jazz",
    "blues",
    "metal",
    "punk",
    "country",
    "folk",
    "hip-hop",
    "dance-electronic",
    "soul",
    "reggae",
    "latin",
    "soundtrack",
    "classical",
)
PROGRESSION_OPERATORS = (
    "sevenths",
    "tonic_pedal",
    "negative_harmony",
    "double_time",
    "half_time",
    "step_up",
)
MIN_LENGTH, MAX_LENGTH = 3, 8


@dataclass(frozen=True)
class HarmonyIntent:
    moods: tuple[str, ...] = ()
    mode: Mode | None = None
    genre: str = ""
    kind: str = ""
    audacity: float | None = None
    length: int | None = None
    operators: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "moods": list(self.moods),
            "mode": self.mode.value if self.mode else None,
            "genre": self.genre,
            "kind": self.kind,
            "audacity": self.audacity,
            "length": self.length,
            "operators": list(self.operators),
        }

    @property
    def empty(self) -> bool:
        return self == HarmonyIntent()


def validate_intent(data: Any) -> HarmonyIntent:
    """Any dict (e.g. an LLM answer) -> a valid intent; unknown values are dropped."""
    if not isinstance(data, dict):
        return HarmonyIntent()

    def strings(value: Any, allowed: tuple[str, ...]) -> tuple[str, ...]:
        items = value if isinstance(value, list) else [value] if isinstance(value, str) else []
        out: list[str] = []
        for item in items:
            name = str(item).strip().lower()
            if name in allowed and name not in out:
                out.append(name)
        return tuple(out)

    mode_value = str(data.get("mode") or "").strip().lower()
    mode = Mode(mode_value) if mode_value in ("major", "minor") else None
    genre = strings(data.get("genre"), GENRES)
    kind = strings(data.get("kind", data.get("section")), PART_ORDER)
    audacity: float | None = None
    raw = data.get("audacity")
    if isinstance(raw, int | float) and not isinstance(raw, bool):
        audacity = round(min(1.0, max(0.0, float(raw))), 2)
    length: int | None = None
    raw = data.get("length")
    if isinstance(raw, int | float) and not isinstance(raw, bool):
        length = int(min(MAX_LENGTH, max(MIN_LENGTH, round(raw))))
    return HarmonyIntent(
        moods=strings(data.get("moods"), MOODS)[:3],
        mode=mode,
        genre=genre[0] if genre else "",
        kind=kind[0] if kind else "",
        audacity=audacity,
        length=length,
        operators=strings(data.get("operators"), PROGRESSION_OPERATORS),
    )


def normalize_text(text: str) -> str:
    """Lowercase, no accents, apostrophes and punctuation as spaces, single spaces."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9#+\- ]+", " ", text)
    return f" {' '.join(text.split())} "


# Each entry: keywords (matched as whole words or phrases after `normalize_text`) -> value.
_MOOD_WORDS: dict[str, tuple[str, ...]] = {
    "bright": ("solare", "luminoso", "luminosa", "allegro", "allegra", "felice", "gioioso",
               "gioiosa", "happy", "bright", "sunny", "cheerful"),
    "uplifting": ("che si apre", "arioso", "ariosa", "liberatorio", "speranza", "speranzoso",
                  "decolla", "inno", "uplifting", "hopeful", "anthem", "anthemic"),
    "melancholic": ("malinconico", "malinconica", "malinconia", "triste", "sad",
                    "melancholic", "melancholy", "blue"),
    "nostalgic": ("nostalgico", "nostalgica", "nostalgia", "ricordo", "vintage", "retro",
                  "nostalgic"),
    "dreamy": ("sognante", "onirico", "onirica", "etereo", "eterea", "dreamy", "ethereal",
               "lofi", "lo-fi", "ambient"),
    "romantic": ("romantico", "romantica", "amore", "tenero", "tenera", "romantic", "love"),
    "dark": ("cupo", "cupa", "oscuro", "oscura", "scuro", "scura", "dark", "gloomy",
             "minaccioso", "minacciosa"),
    "epic": ("epico", "epica", "grandioso", "grandiosa", "eroico", "eroica", "epic",
             "cinematic", "cinematografico", "trailer", "heroic"),
    "tense": ("teso", "tesa", "tensione", "suspense", "ansia", "drammatico", "drammatica",
              "tense", "dramatic", "tension"),
    "mysterious": ("misterioso", "misteriosa", "mistero", "enigmatico", "esotico", "esotica",
                   "mysterious", "exotic"),
    "groovy": ("groove", "groovy", "funky", "ballabile", "danzante"),
    "calm": ("calmo", "calma", "rilassato", "rilassata", "tranquillo", "tranquilla", "sereno",
             "serena", "pacato", "calm", "chill", "relaxed", "peaceful"),
}  # fmt: skip
_GENRE_WORDS: dict[str, tuple[str, ...]] = {
    "pop": ("pop",),
    "rock": ("rock",),
    "jazz": ("jazz", "jazzy", "swing"),
    "blues": ("blues",),
    "metal": ("metal",),
    "punk": ("punk",),
    "country": ("country",),
    "folk": ("folk", "cantautore", "cantautorale", "acustico", "acoustic"),
    "hip-hop": ("hip hop", "hip-hop", "hiphop", "rap", "trap"),
    "dance-electronic": ("edm", "elettronica", "elettronico", "electronic", "house", "techno",
                         "dance", "synthwave"),
    "soul": ("soul", "r&b", "rnb", "neo soul", "gospel"),
    "reggae": ("reggae",),
    "latin": ("latino", "latina", "latin", "bossa", "salsa", "flamenco"),
    "soundtrack": ("colonna sonora", "soundtrack", "film", "videogioco", "game"),
    "classical": ("classica", "classico", "classical", "barocco", "baroque"),
}  # fmt: skip
_KIND_WORDS: dict[str, tuple[str, ...]] = {
    "intro": ("intro", "introduzione"),
    "verse": ("strofa", "verse"),
    "prechorus": ("pre ritornello", "pre-ritornello", "prechorus", "pre-chorus", "pre chorus"),
    "chorus": ("ritornello", "chorus", "refrain", "hook"),
    "bridge": ("ponte", "bridge", "special"),
    "outro": ("finale", "outro", "coda", "chiusura"),
}
_OPERATOR_WORDS: dict[str, tuple[str, ...]] = {
    "sevenths": ("settime", "settima", "sevenths", "seventh", "7th", "accordi ricchi"),
    "tonic_pedal": ("pedale", "pedal"),
    "negative_harmony": ("armonia negativa", "negative harmony"),
    "double_time": ("cambi veloci", "cambi rapidi", "fast changes", "due accordi per battuta"),
    "half_time": ("cambi lenti", "slow changes", "accordi lunghi"),
    "step_up": ("modula", "modulazione", "su di un tono", "key change", "modulate"),
}
_BOLD = ("audace", "sperimentale", "insolito", "insolita", "strano", "strana", "sorprendente",
         "coraggioso", "coraggiosa", "bold", "experimental", "unusual", "weird", "surprising",
         "avventuroso", "adventurous")  # fmt: skip
_SAFE = ("classico giro", "semplice", "standard", "tipico", "tipica", "scontato", "cliche",
         "simple", "common", "typical", "safe", "radiofonico", "catchy",
         "orecchiabile")  # fmt: skip
_MID = ("originale", "personale", "un po diverso", "diverso dal solito", "original", "fresh",
        "fresco", "fresca")  # fmt: skip
_NUMBERS = {"tre": 3, "three": 3, "quattro": 4, "four": 4, "cinque": 5, "five": 5, "sei": 6,
            "six": 6, "sette": 7, "seven": 7, "otto": 8, "eight": 8}  # fmt: skip


def _has(text: str, words: tuple[str, ...]) -> bool:
    return any(f" {w} " in text for w in words)


class KeywordHarmonyInterpreter:
    """Offline interpretation of Italian / English keywords. Deterministic."""

    source = "keywords"

    def interpret(self, text: str) -> HarmonyIntent:
        t = normalize_text(text)
        moods = [m for m, words in _MOOD_WORDS.items() if _has(t, words)]
        genre = next((g for g, words in _GENRE_WORDS.items() if _has(t, words)), "")
        kind = next((k for k, words in _KIND_WORDS.items() if _has(t, words)), "")
        if kind == "chorus" and _has(t, _KIND_WORDS["prechorus"]):
            kind = "prechorus"
        mode = None
        if _has(t, ("minore", "minor", "in minore")):
            mode = Mode.MINOR
        elif _has(t, ("maggiore", "major", "in maggiore")):
            mode = Mode.MAJOR
        audacity = None
        very = _has(t, ("molto", "very", "super", "estremamente", "really"))
        if _has(t, _BOLD):
            audacity = 0.95 if very else 0.8
        elif _has(t, _MID):
            audacity = 0.5
        elif _has(t, _SAFE):
            audacity = 0.1
        length = None
        match = re.search(r" (\d+|" + "|".join(_NUMBERS) + r") (accordi|chords|chord)\b", t)
        if match:
            raw = match.group(1)
            length = int(raw) if raw.isdigit() else _NUMBERS[raw]
        operators = [op for op, words in _OPERATOR_WORDS.items() if _has(t, words)]
        return validate_intent(
            {
                "moods": moods,
                "mode": mode.value if mode else None,
                "genre": genre,
                "kind": kind,
                "audacity": audacity,
                "length": length,
                "operators": operators,
            }
        )


def intent_schema() -> dict[str, Any]:
    """JSON schema of `HarmonyIntent` for structured LLM output."""
    return {
        "type": "object",
        "properties": {
            "moods": {"type": "array", "items": {"type": "string", "enum": list(MOODS)}},
            "mode": {"type": ["string", "null"], "enum": ["major", "minor", None]},
            "genre": {"type": "string", "enum": ["", *GENRES]},
            "kind": {"type": "string", "enum": ["", *PART_ORDER]},
            "audacity": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
            "length": {"type": ["integer", "null"], "minimum": MIN_LENGTH, "maximum": MAX_LENGTH},
            "operators": {
                "type": "array",
                "items": {"type": "string", "enum": list(PROGRESSION_OPERATORS)},
            },
        },
        "required": ["moods", "mode", "genre", "kind", "audacity", "length", "operators"],
    }
