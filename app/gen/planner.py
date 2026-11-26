"""Planners (CLAUDE.md section 6.6): chord progressions and, later (C4), whole-song plans.

The generator must never depend on a specific planner. `RuleBasedPlanner` needs no network and
is the default; an LLM planner (local Ollama) arrives in C4 behind the same interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, TypedDict

from app.core.harmony import chord_from_roman
from app.core.model import ChordSlot, Key, Mode

SECTION_KINDS = ("intro", "verse", "prechorus", "chorus", "bridge", "outro")


class Plan(TypedDict):
    chord_grid: list[dict[str, Any]]
    sections: list[dict[str, Any]]
    per_bar_controls: list[dict[str, Any]]


class Planner(Protocol):
    def suggest_progressions(
        self, key: Key, genre: str, section_kind: str, bars: int, n: int
    ) -> list[list[ChordSlot]]: ...


@dataclass(frozen=True)
class Template:
    numerals: tuple[str, ...]  # one chord per bar, relative to the key's own scale
    kinds: frozenset[str] = frozenset()  # section kinds it suits best (empty = any)
    genres: frozenset[str] = frozenset()  # genres it suits best (empty = any)


def _t(numerals: str, kinds: str = "", genres: str = "") -> Template:
    return Template(tuple(numerals.split()), frozenset(kinds.split()), frozenset(genres.split()))


# Ordered by general usefulness: ties in the ranking keep this order.
TEMPLATES: dict[Mode, tuple[Template, ...]] = {
    Mode.MAJOR: (
        _t("I V vi IV", "chorus verse", "pop rock country folk"),
        _t("vi IV I V", "chorus verse", "pop dance-electronic hip-hop"),
        _t("I vi IV V", "verse", "pop country folk"),
        _t("IV V iii vi", "prechorus chorus", "pop dance-electronic"),
        _t("ii V I I", "verse bridge", "jazz"),
        _t("ii7 V7 Imaj7 Imaj7", "verse chorus", "jazz"),
        _t("I IV I V", "verse", "rock blues country folk punk"),
        _t("I bVII IV I", "chorus bridge", "rock metal punk"),
        _t("IV V vi vi", "prechorus", "pop"),
        _t("ii IV V V", "prechorus", "pop rock"),
        _t("vi V IV V", "bridge", "pop rock"),
        _t("IV IV I I", "bridge", "pop folk country"),
        _t("I I IV IV", "intro outro", ""),
        _t("Imaj7 IVmaj7 Imaj7 IVmaj7", "intro verse", "jazz soundtrack latin"),
        _t("I IV vi V", "verse chorus", "pop"),
        _t("IV I V vi", "bridge chorus", "pop"),
    ),
    Mode.MINOR: (
        _t("i VI III VII", "chorus verse", "pop rock dance-electronic"),
        _t("i VII VI VII", "verse chorus", "rock metal"),
        _t("i iv VII III", "verse", "pop hip-hop"),
        _t("VI VII i i", "prechorus chorus", "pop rock dance-electronic"),
        _t("i VI iv V", "chorus bridge", "pop soundtrack classical"),
        _t("i iv v i", "verse", "folk blues"),
        _t("iiø7 V7 i i", "verse bridge", "jazz latin"),
        _t("i7 iv7 i7 V7", "verse", "jazz blues"),
        _t("i VI VII i", "verse", "metal soundtrack"),
        _t("iv VI VII VII", "prechorus", "pop rock"),
        _t("VI III VII iv", "bridge", "pop soundtrack"),
        _t("i i VI VI", "intro outro", ""),
        _t("i VII VI V", "chorus", "rock latin metal"),
        _t("i III VII iv", "chorus", "pop hip-hop"),
        _t("i iv i v", "intro verse", "hip-hop soundtrack"),
    ),
}

# Section-end cadences (last bar), applied when the section is at least 4 bars long.
_CADENCE: dict[str, dict[Mode, str]] = {
    "outro": {Mode.MAJOR: "I", Mode.MINOR: "i"},
    "prechorus": {Mode.MAJOR: "V", Mode.MINOR: "V"},
}


def normalize_kind(kind: str) -> str:
    kind = kind.strip().lower().replace("-", "").replace(" ", "")
    aliases = {"pre": "prechorus", "strofa": "verse", "ritornello": "chorus", "ponte": "bridge"}
    return aliases.get(kind, kind)


class RuleBasedPlanner:
    """Progressions from a curated table, ranked by section kind and genre. Deterministic."""

    def suggest_progressions(
        self, key: Key, genre: str, section_kind: str, bars: int, n: int = 5
    ) -> list[list[ChordSlot]]:
        if bars < 1 or n < 1:
            return []
        kind = normalize_kind(section_kind)
        genre = genre.strip().lower()
        ranked = sorted(
            enumerate(TEMPLATES[key.mode]),
            key=lambda it: (
                -(2 * (kind in it[1].kinds) + (genre in it[1].genres)),
                it[0],
            ),
        )
        out: list[list[ChordSlot]] = []
        for _, template in ranked:
            grid = self._expand(template, key, kind, bars)
            if grid not in out:
                out.append(grid)
            if len(out) == n:
                break
        return out

    @staticmethod
    def _expand(template: Template, key: Key, kind: str, bars: int) -> list[ChordSlot]:
        chords = [chord_from_roman(numeral, key) for numeral in template.numerals]
        grid = [chords[i % len(chords)] for i in range(bars)]
        cadence = _CADENCE.get(kind, {}).get(key.mode)
        if cadence and bars >= 4:
            grid[-1] = chord_from_roman(cadence, key)
        return grid
