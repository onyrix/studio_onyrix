"""Block-chord voicing with simple voice leading, for auditioning progressions. Pure.

Each chord becomes a root in the bass register plus up to four upper voices in close
position; among the inversions that fit the range, the one closest to the previous voicing
(smallest total movement) is chosen, so the upper voices move smoothly like a pianist's.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.core.model import ChordSlot, Note
from app.core.progression import ChordSpan

UPPER_LOW, UPPER_HIGH = 52, 79  # E3..G5
BASS_LOW = 36  # C2; the root lands in C2..B2
MAX_UPPER = 4


def _upper_pitch_classes(chord: ChordSlot) -> list[int]:
    """Chord tones above the root, root first; with more than four, drop the fifth first."""
    pcs = sorted(chord.pitch_class_set, key=lambda pc: (pc - chord.root) % 12)
    if len(pcs) > MAX_UPPER:
        fifth = (chord.root + 7) % 12
        if fifth in pcs:
            pcs.remove(fifth)
        pcs = pcs[:MAX_UPPER]
    return pcs


def _candidates(pcs: list[int]) -> list[list[int]]:
    """Close-position voicings (every inversion, every octave) inside the upper range."""
    out = []
    for rotation in range(len(pcs)):
        order = pcs[rotation:] + pcs[:rotation]
        for base in range(UPPER_LOW, UPPER_LOW + 12):
            if base % 12 != order[0]:
                continue
            for octave in (0, 12):
                voicing = [base + octave]
                for pc in order[1:]:
                    nxt = voicing[-1] + 1
                    while nxt % 12 != pc:
                        nxt += 1
                    voicing.append(nxt)
                if voicing[-1] <= UPPER_HIGH:
                    out.append(voicing)
    return out


def _cost(voicing: list[int], previous: list[int] | None) -> float:
    if previous is None:
        center = (UPPER_LOW + UPPER_HIGH) / 2
        return abs(sum(voicing) / len(voicing) - center)
    a, b = sorted(voicing), sorted(previous)
    if len(a) == len(b):
        return float(sum(abs(x - y) for x, y in zip(a, b, strict=True)))
    return abs(sum(a) / len(a) - sum(b) / len(b)) * max(len(a), len(b))


def voice_progression(
    spans: Sequence[ChordSpan], velocity: int = 80, bass: bool = True
) -> tuple[Note, ...]:
    notes: list[Note] = []
    previous: list[int] | None = None
    for span in spans:
        pcs = _upper_pitch_classes(span.chord)
        options = _candidates(pcs)
        if not options:
            continue
        voicing = min(options, key=lambda v: (_cost(v, previous), v))
        duration = span.end - span.start
        notes.extend(Note(span.start, p, duration, velocity) for p in voicing)
        if bass:
            root = BASS_LOW + (span.chord.root - BASS_LOW) % 12
            notes.append(Note(span.start, root, duration, velocity))
        previous = voicing
    return tuple(sorted(notes, key=lambda n: (n.t, n.p)))
