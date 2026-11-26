"""Deterministic post-processing of candidate notes (CLAUDE.md section 6.4). Pure and idempotent.

Order: clamp pitch to the role range (octave shifts), snap onsets and ends to the grid, drop/trim
at the clip end, normalise velocities, remove duplicates, cap polyphony per onset (monophony for
mono roles), then trim same-pitch overlaps (any overlap for mono roles).
"""

from __future__ import annotations

import random
from collections.abc import Iterable, Sequence

from app.core.model import ChordSlot, Note, Role
from app.core.roles import RoleSpec
from app.core.timebase import FOUR_FOUR, PPQ, STEP_TICKS, TimeSignature, bar_ticks

TRIPLET_TICKS = PPQ // 3  # 8th-note triplet = 160 ticks


def _grid_units(triplets: bool) -> tuple[int, ...]:
    return (STEP_TICKS, TRIPLET_TICKS) if triplets else (STEP_TICKS,)


def snap(ticks: int, triplets: bool = False) -> int:
    """Nearest grid point; ties resolve to the earlier point."""
    best = 0
    best_dist: int | None = None
    for unit in _grid_units(triplets):
        down = (ticks // unit) * unit
        for point in (down, down + unit):
            dist = abs(point - ticks)
            if best_dist is None or dist < best_dist or (dist == best_dist and point < best):
                best, best_dist = point, dist
    return max(0, best)


def next_grid_point(ticks: int, triplets: bool = False) -> int:
    """Smallest grid point strictly greater than `ticks`."""
    return min((ticks // unit + 1) * unit for unit in _grid_units(triplets))


def clamp_pitch(pitch: int, low: int, high: int) -> int:
    """Move `pitch` into [low, high] by octaves; clamp if the range is narrower than an octave."""
    while pitch < low and pitch + 12 <= 127:
        pitch += 12
    while pitch > high and pitch - 12 >= 0:
        pitch -= 12
    return min(max(pitch, low), high)


def postprocess(
    notes: Iterable[Note], spec: RoleSpec, clip_ticks: int, triplets: bool = False
) -> tuple[Note, ...]:
    if clip_ticks <= 0:
        return ()

    # 1-4: pitch, grid, clip end, velocity.
    shaped: list[Note] = []
    for note in notes:
        pitch = note.p if spec.is_drum else clamp_pitch(note.p, spec.low, spec.high)
        start = snap(note.t, triplets)
        if start >= clip_ticks:
            continue
        end = snap(note.t + note.d, triplets)
        if end <= start:
            end = next_grid_point(start, triplets)
        end = min(end, clip_ticks)
        velocity = min(max(note.v, 1), 127)
        shaped.append(Note(t=start, p=pitch, d=end - start, v=velocity))

    # 5: duplicates (same onset and pitch): keep the loudest, then the longest.
    unique: dict[tuple[int, int], Note] = {}
    for note in shaped:
        key = (note.t, note.p)
        current = unique.get(key)
        if current is None or (note.v, note.d) > (current.v, current.d):
            unique[key] = note

    # 6: polyphony cap per onset. Mono bass keeps the lowest pitch, other roles the loudest
    # (ties: highest pitch for lead-like roles).
    by_onset: dict[int, list[Note]] = {}
    for note in unique.values():
        by_onset.setdefault(note.t, []).append(note)
    kept: list[Note] = []
    for group in by_onset.values():
        if spec.monophonic and spec.role.value == "bass":
            group.sort(key=lambda n: (n.p, -n.v))
        else:
            group.sort(key=lambda n: (-n.v, -n.p))
        kept.extend(group[: spec.max_polyphony])

    # 7: overlaps. Mono roles: any overlap; others: same pitch only.
    kept.sort(key=lambda n: (n.t, n.p))
    result: list[Note] = []
    if spec.monophonic:
        for i, note in enumerate(kept):
            end = note.end
            if i + 1 < len(kept):
                end = min(end, kept[i + 1].t)
            result.append(Note(t=note.t, p=note.p, d=end - note.t, v=note.v))
    else:
        next_start: dict[int, int] = {}
        for note in reversed(kept):
            end = min(note.end, next_start.get(note.p, note.end))
            result.append(Note(t=note.t, p=note.p, d=end - note.t, v=note.v))
            next_start[note.p] = note.t
        result.reverse()
    return tuple(result)


HARMONY_LEVELS = ("off", "light", "normal", "strict")


def _nearest_in(pitch: int, pcs: frozenset[int], low: int, high: int) -> int | None:
    """Closest pitch in [low, high] whose pitch class is in `pcs`; ties go down."""
    for distance in range(12):
        for candidate in (pitch - distance, pitch + distance):
            if low <= candidate <= high and candidate % 12 in pcs:
                return candidate
    return None


def harmonic_snap(
    notes: Iterable[Note],
    chords: Sequence[ChordSlot | None],
    spec: RoleSpec,
    clip_ticks: int,
    ts: TimeSignature = FOUR_FOUR,
    level: str = "normal",
    bass_root: bool = True,
) -> tuple[Note, ...]:
    """Move out-of-chord notes to the nearest chord tone in the role range (CLAUDE.md 6.8).

    `chords` has one entry per bar (cycled; None = no harmony for that bar). Levels:
    - off: unchanged;
    - light: only notes starting on a bar's downbeat;
    - normal: notes on beats for monophonic roles, every onset for polyphonic roles; notes
      sounding into a bar whose chord excludes them are trimmed at the bar line;
    - strict: every onset for every role, plus the trimming.
    `bass_root` puts the bass note starting on each downbeat on the chord root.
    Drums are never touched. Deterministic and idempotent; run `postprocess` afterwards to
    remove duplicates the moves may create.
    """
    if level not in HARMONY_LEVELS:
        raise ValueError(f"unknown harmony level {level!r}")
    result = tuple(notes)
    if spec.is_drum or level == "off" or not any(chords):
        return result
    bar_len = bar_ticks(ts)
    beat = PPQ * 4 // ts.denominator

    def chord_at(tick: int) -> ChordSlot | None:
        return chords[(tick // bar_len) % len(chords)]

    out = []
    for note in result:
        chord = chord_at(note.t)
        pitch = note.p
        end = note.end
        if chord is not None:
            offset = note.t % bar_len
            if level == "light":
                applies = offset == 0
            elif level == "strict" or not spec.monophonic:
                applies = True
            else:
                applies = offset % beat == 0
            target: frozenset[int] | None = None
            if spec.role is Role.BASS and bass_root and offset == 0:
                target = frozenset({chord.root})
            elif applies and pitch % 12 not in chord.pitch_class_set:
                target = chord.pitch_class_set
            if target is not None:
                moved = _nearest_in(pitch, target, spec.low, spec.high)
                pitch = pitch if moved is None else moved
        if level in ("normal", "strict"):
            boundary = (note.t // bar_len + 1) * bar_len
            while boundary < min(end, clip_ticks):
                following = chord_at(boundary)
                if following is not None and pitch % 12 not in following.pitch_class_set:
                    end = boundary
                    break
                boundary += bar_len
        out.append(Note(t=note.t, p=pitch, d=end - note.t, v=note.v))
    return tuple(out)


def humanize(
    notes: Iterable[Note],
    seed: int,
    clip_ticks: int,
    timing_ticks: int = 8,
    velocity_range: int = 6,
) -> tuple[Note, ...]:
    """Optional small timing/velocity jitter, applied after post-processing. Off by default."""
    rng = random.Random(seed)
    out = []
    for note in notes:
        start = min(max(0, note.t + rng.randint(-timing_ticks, timing_ticks)), clip_ticks - 1)
        end = min(max(start + 1, note.end), clip_ticks)
        velocity = min(max(note.v + rng.randint(-velocity_range, velocity_range), 1), 127)
        out.append(Note(t=start, p=note.p, d=end - start, v=velocity))
    return tuple(out)
