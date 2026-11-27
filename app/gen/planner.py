"""Planners (CLAUDE.md section 6.6): chord progressions and, later (C4), whole-song plans.

The generator must never depend on a specific planner. `RuleBasedPlanner` needs no network and
is the default: it draws from the curated library (`core.library`). An LLM planner (local
Ollama) arrives behind the same interface.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Protocol, TypedDict

from app.core import library
from app.core.library import LibraryProgression
from app.core.model import Key
from app.core.progression import ChordEvent
from app.core.timebase import FOUR_FOUR, TimeSignature

SECTION_KINDS = library.PART_ORDER


class Plan(TypedDict):
    chord_grid: list[dict[str, Any]]
    sections: list[dict[str, Any]]
    per_bar_controls: list[dict[str, Any]]


@dataclass(frozen=True)
class ProgressionSuggestion:
    source: LibraryProgression
    events: list[ChordEvent]


class Planner(Protocol):
    def suggest_progressions(
        self,
        key: Key,
        genre: str,
        section_kind: str,
        bars: int,
        n: int,
        moods: Iterable[str] = (),
        ts: TimeSignature = FOUR_FOUR,
    ) -> list[ProgressionSuggestion]: ...


_KIND_ALIASES = {
    "pre": "prechorus",
    "prerit": "prechorus",
    "preritornello": "prechorus",
    "strofa": "verse",
    "ritornello": "chorus",
    "refrain": "chorus",
    "hook": "chorus",
    "ponte": "bridge",
    "special": "bridge",
    "finale": "outro",
    "coda": "outro",
    "ending": "outro",
}


def normalize_kind(kind: str) -> str:
    kind = "".join(ch for ch in kind.lower() if ch.isalpha())
    return _KIND_ALIASES.get(kind, kind)


def kind_from_name(name: str) -> str:
    """Section kind guessed from a section name such as "Chorus 2" or "Strofa A"; "" if unknown."""
    words = name.lower().replace("-", "").split()
    for candidate in ("".join(words), *(words[:1])):
        kind = normalize_kind(candidate)
        if kind in SECTION_KINDS:
            return kind
    return ""


class RuleBasedPlanner:
    """Progressions from the curated library, ranked by section kind, genre, mood and fit."""

    def suggest_progressions(
        self,
        key: Key,
        genre: str,
        section_kind: str,
        bars: int,
        n: int = 5,
        moods: Iterable[str] = (),
        ts: TimeSignature = FOUR_FOUR,
    ) -> list[ProgressionSuggestion]:
        if bars < 1 or n < 1:
            return []
        found = library.search(
            key.mode, normalize_kind(section_kind), genre.strip().lower(), moods, bars, ts
        )
        return [ProgressionSuggestion(p, library.realize(p.numerals, key, ts)) for p in found[:n]]
