"""GM drum map, step-grid <-> notes, drum pattern checks. Pure."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from app.core.model import Note
from app.core.timebase import (
    FOUR_FOUR,
    PPQ,
    STEP_TICKS,
    TimeSignature,
    bar_ticks,
    steps_per_bar,
)

KICK = 36
SNARE = 38
CLAP = 39
CLOSED_HAT = 42
PEDAL_HAT = 44
OPEN_HAT = 46
LOW_TOM = 45
MID_TOM = 47
HIGH_TOM = 50
CRASH = 49
RIDE = 51

DRUM_MAP: dict[str, int] = {
    "kick": KICK,
    "snare": SNARE,
    "clap": CLAP,
    "closed_hat": CLOSED_HAT,
    "pedal_hat": PEDAL_HAT,
    "open_hat": OPEN_HAT,
    "low_tom": LOW_TOM,
    "mid_tom": MID_TOM,
    "high_tom": HIGH_TOM,
    "crash": CRASH,
    "ride": RIDE,
}

KICKS = frozenset({35, KICK})
BACKBEAT = frozenset({SNARE, 40, CLAP})  # acoustic snare, electric snare, clap

# Genres where a kick on every quarter note is expected (lower-case labels).
FOUR_ON_FLOOR_GENRES = frozenset({"dance-electronic", "house", "techno", "edm", "disco", "trance"})


def is_four_on_floor(genre: str | None) -> bool:
    return (genre or "").strip().lower() in FOUR_ON_FLOOR_GENRES


def notes_to_grid(
    notes: Iterable[Note], bars: int, ts: TimeSignature = FOUR_FOUR
) -> dict[int, list[bool]]:
    """Map pitch -> one bool per 16th step over `bars` bars (onsets off the grid round down)."""
    total = bars * steps_per_bar(ts)
    grid: dict[int, list[bool]] = {}
    for note in notes:
        step = note.t // STEP_TICKS
        if step < total:
            grid.setdefault(note.p, [False] * total)[step] = True
    return grid


def grid_to_notes(
    grid: Mapping[int, Sequence[bool]], velocity: int = 100, duration: int = STEP_TICKS
) -> tuple[Note, ...]:
    notes = [
        Note(t=step * STEP_TICKS, p=pitch, d=duration, v=velocity)
        for pitch, steps in grid.items()
        for step, on in enumerate(steps)
        if on
    ]
    return tuple(sorted(notes, key=lambda n: (n.t, n.p)))


def onsets(notes: Iterable[Note], pitches: frozenset[int]) -> frozenset[int]:
    return frozenset(n.t for n in notes if n.p in pitches)


def missing_downbeat_kick(notes: Iterable[Note], bars: int, ts: TimeSignature = FOUR_FOUR) -> bool:
    kicks = onsets(notes, KICKS)
    return any(bar * bar_ticks(ts) not in kicks for bar in range(bars))


def pattern_coverage(
    notes: Iterable[Note], bars: int, four_on_floor: bool, ts: TimeSignature = FOUR_FOUR
) -> float:
    """Fraction of expected pattern hits present.

    Expected per bar: a kick on every beat (four-on-the-floor) or on the downbeat (otherwise),
    plus, in 4/4, a backbeat (snare or clap) on beats 2 and 4.
    """
    notes = tuple(notes)
    kicks = onsets(notes, KICKS)
    backbeats = onsets(notes, BACKBEAT)
    beat = PPQ * 4 // ts.denominator
    expected = 0
    present = 0
    for bar in range(bars):
        start = bar * bar_ticks(ts)
        kick_beats = range(ts.numerator) if four_on_floor else range(1)
        for b in kick_beats:
            expected += 1
            present += start + b * beat in kicks
        if ts == FOUR_FOUR:
            for b in (1, 3):
                expected += 1
                present += start + b * beat in backbeats
    return present / expected if expected else 1.0
