"""Chord progressions with harmonic rhythm: chord events, their timeline and a text syntax. Pure.

A progression is a list of `ChordEvent`s; each lasts `beats` beats (None = one whole bar, which
keeps the old one-chord-per-bar grids valid). A section cycles its progression over its length,
giving a `ChordSpan` timeline in clip-relative ticks that the generator, the harmonic snap and the
scorer all read.

Text syntax (one token per chord, `|` bar lines are optional and ignored):
    Am           one bar
    C*2          two bars
    (Am F)       one bar split equally between the chords
    G:3          three beats
    %            repeat the previous chord for one bar
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from app.core.harmony import chord_slot_from_dict, chord_slot_to_dict, parse_chord
from app.core.harmony import chord_symbol as _symbol
from app.core.model import ChordSlot, Key
from app.core.timebase import FOUR_FOUR, PPQ, TimeSignature, bar_ticks

MAX_BEATS = 64


@dataclass(frozen=True)
class ChordEvent:
    chord: ChordSlot
    beats: int | None = None  # None = one whole bar

    def __post_init__(self) -> None:
        if self.beats is not None and not 1 <= self.beats <= MAX_BEATS:
            raise ValueError(f"beats must be in 1..{MAX_BEATS}, got {self.beats}")

    def length(self, ts: TimeSignature) -> int:
        return bar_ticks(ts) if self.beats is None else self.beats * beat_ticks(ts)


@dataclass(frozen=True)
class ChordSpan:
    start: int  # clip-relative ticks, inclusive
    end: int  # exclusive
    chord: ChordSlot


def beat_ticks(ts: TimeSignature) -> int:
    return PPQ * 4 // ts.denominator


# ---- Storage ----------------------------------------------------------------------------


def event_to_dict(event: ChordEvent) -> dict[str, Any]:
    data: dict[str, Any] = chord_slot_to_dict(event.chord)
    if event.beats is not None:
        data["beats"] = event.beats
    return data


def event_from_dict(data: dict[str, Any]) -> ChordEvent:
    beats = data.get("beats")
    return ChordEvent(chord_slot_from_dict(data), None if beats is None else int(beats))


def normalize_events(events: Sequence[ChordEvent], ts: TimeSignature) -> list[ChordEvent]:
    """A chord lasting exactly one bar is stored without `beats`."""
    per_bar = ts.numerator
    return [ChordEvent(e.chord, None if e.beats == per_bar else e.beats) for e in events]


# ---- Timeline ---------------------------------------------------------------------------


def chord_timeline(
    events: Sequence[ChordEvent], bars: int, ts: TimeSignature = FOUR_FOUR
) -> tuple[ChordSpan, ...]:
    """Cycle `events` over `bars` bars; the last span is cut at the section end. No events =
    no harmony (empty timeline)."""
    total = bars * bar_ticks(ts)
    if not events or total <= 0:
        return ()
    spans = []
    tick = 0
    i = 0
    while tick < total:
        event = events[i % len(events)]
        end = min(tick + event.length(ts), total)
        spans.append(ChordSpan(tick, end, event.chord))
        tick = end
        i += 1
    return tuple(spans)


def chord_at(spans: Sequence[ChordSpan], tick: int) -> ChordSlot | None:
    for span in spans:
        if span.start <= tick < span.end:
            return span.chord
    return None


def span_at(spans: Sequence[ChordSpan], tick: int) -> ChordSpan | None:
    for span in spans:
        if span.start <= tick < span.end:
            return span
    return None


def chords_in_bar(spans: Sequence[ChordSpan], bar: int, ts: TimeSignature) -> list[ChordSlot]:
    start, end = bar * bar_ticks(ts), (bar + 1) * bar_ticks(ts)
    return [s.chord for s in spans if s.start < end and s.end > start]


def bar_spans(
    chords: Sequence[ChordSlot | None], ts: TimeSignature = FOUR_FOUR
) -> tuple[ChordSpan, ...]:
    """One chord per bar (None = no harmony in that bar): the pre-harmonic-rhythm grid shape."""
    length = bar_ticks(ts)
    return tuple(
        ChordSpan(i * length, (i + 1) * length, c) for i, c in enumerate(chords) if c is not None
    )


# ---- Text syntax ------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"\(|\)|[^\s(),|]+")
_SUFFIX_RE = re.compile(r"^(?P<symbol>[^*:]+)(?:\*(?P<bars>\d+)|:(?P<beats>\d+))?$")


def parse_progression(
    text: str,
    ts: TimeSignature = FOUR_FOUR,
    chord_parser: Callable[[str], ChordSlot] = parse_chord,
) -> list[ChordEvent]:
    """Parse the text syntax in the module docstring. Raises ValueError with a readable reason.

    `chord_parser` reads one chord token: chord symbols by default; pass
    `lambda n: chord_from_roman(n, key)` for roman numerals (`I V vi IV`, `ii7 V7 Imaj7*2`).
    """
    per_bar = ts.numerator
    events: list[ChordEvent] = []
    group: list[ChordSlot] | None = None
    for token in _TOKEN_RE.findall(text):
        if token == "(":
            if group is not None:
                raise ValueError("nested parentheses are not allowed")
            group = []
        elif token == ")":
            if not group:
                raise ValueError("empty or unmatched parentheses")
            if per_bar % len(group):
                raise ValueError(
                    f"{len(group)} chords cannot split a bar of {per_bar} beats evenly"
                )
            events.extend(ChordEvent(c, per_bar // len(group)) for c in group)
            group = None
        elif token == "%":
            if group is not None or not events:
                raise ValueError("'%' repeats the previous chord and needs one before it")
            events.append(ChordEvent(events[-1].chord, per_bar))
        else:
            match = _SUFFIX_RE.match(token)
            if not match:
                raise ValueError(f"invalid chord token: {token!r}")
            chord = chord_parser(match["symbol"])
            if group is not None:
                if match["bars"] or match["beats"]:
                    raise ValueError("durations are not allowed inside parentheses")
                group.append(chord)
            elif match["bars"]:
                events.append(ChordEvent(chord, int(match["bars"]) * per_bar))
            elif match["beats"]:
                events.append(ChordEvent(chord, int(match["beats"])))
            else:
                events.append(ChordEvent(chord, per_bar))
    if group is not None:
        raise ValueError("unclosed parenthesis")
    return normalize_events(events, ts)


def progression_text(
    events: Sequence[ChordEvent],
    key: Key | None = None,
    ts: TimeSignature = FOUR_FOUR,
    namer: Callable[[ChordSlot], str] | None = None,
) -> str:
    """Inverse of `parse_progression` (canonical form). `namer` names each chord: chord
    symbols spelled for `key` by default; pass `lambda c: roman_numeral(c, key)` for numerals."""
    per_bar = ts.numerator

    def chord_symbol(chord: ChordSlot, key: Key | None) -> str:
        return namer(chord) if namer else _symbol(chord, key)

    out: list[str] = []
    i = 0
    while i < len(events):
        event = events[i]
        beats = per_bar if event.beats is None else event.beats
        if beats < per_bar and per_bar % beats == 0:
            n = per_bar // beats
            group = events[i : i + n]
            if len(group) == n and all(e.beats == beats for e in group):
                out.append("(" + " ".join(chord_symbol(e.chord, key) for e in group) + ")")
                i += n
                continue
        symbol = chord_symbol(event.chord, key)
        if beats == per_bar:
            out.append(symbol)
        elif beats % per_bar == 0:
            out.append(f"{symbol}*{beats // per_bar}")
        else:
            out.append(f"{symbol}:{beats}")
        i += 1
    return " ".join(out)
