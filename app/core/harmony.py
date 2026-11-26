"""Chord symbols -> pitch class sets, key / scale helpers. Pure."""

from __future__ import annotations

import re

from app.core.model import ChordSlot, Key, Mode

NOTE_TO_PC: dict[str, int] = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}

# Intervals in semitones above the root.
QUALITIES: dict[str, tuple[int, ...]] = {
    "": (0, 4, 7),
    "m": (0, 3, 7),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "6": (0, 4, 7, 9),
    "m6": (0, 3, 7, 9),
    "7": (0, 4, 7, 10),
    "maj7": (0, 4, 7, 11),
    "m7": (0, 3, 7, 10),
    "m7b5": (0, 3, 6, 10),
    "dim7": (0, 3, 6, 9),
    "9": (0, 4, 7, 10, 14),
    "maj9": (0, 4, 7, 11, 14),
    "m9": (0, 3, 7, 10, 14),
    "add9": (0, 4, 7, 14),
}

QUALITY_ALIASES: dict[str, str] = {
    "maj": "",
    "M": "",
    "min": "m",
    "-": "m",
    "M7": "maj7",
    "Maj7": "maj7",
    "min7": "m7",
    "-7": "m7",
    "ø": "m7b5",
    "o": "dim",
    "o7": "dim7",
    "+": "aug",
    "sus": "sus4",
}

SCALES: dict[Mode, tuple[int, ...]] = {
    Mode.MAJOR: (0, 2, 4, 5, 7, 9, 11),
    Mode.MINOR: (0, 2, 3, 5, 7, 8, 10),
}

_CHORD_RE = re.compile(r"^([A-G])([#b]?)([^/]*)(?:/([A-G])([#b]?))?$")


def note_pc(letter: str, accidental: str = "") -> int:
    pc = NOTE_TO_PC[letter]
    if accidental == "#":
        pc += 1
    elif accidental == "b":
        pc -= 1
    return pc % 12


def parse_chord(symbol: str) -> ChordSlot:
    """Parse a chord symbol such as `Am7`, `F#m7b5`, `Bbmaj7`, `C/E`.

    Raises ValueError for anything not understood: never silently guess a chord.
    A slash bass note is added to the pitch class set.
    """
    match = _CHORD_RE.match(symbol.strip())
    if not match:
        raise ValueError(f"invalid chord symbol: {symbol!r}")
    letter, accidental, quality, bass_letter, bass_accidental = match.groups()
    quality = QUALITY_ALIASES.get(quality, quality)
    if quality not in QUALITIES:
        raise ValueError(f"unknown chord quality {quality!r} in {symbol!r}")
    root = note_pc(letter, accidental)
    pcs = {(root + interval) % 12 for interval in QUALITIES[quality]}
    if bass_letter:
        pcs.add(note_pc(bass_letter, bass_accidental or ""))
    return ChordSlot(root=root, quality=quality, pitch_class_set=frozenset(pcs))


def scale_pitch_classes(key: Key) -> frozenset[int]:
    return frozenset((key.tonic + interval) % 12 for interval in SCALES[key.mode])


def chord_slot_to_dict(slot: ChordSlot) -> dict[str, object]:
    return {
        "root": slot.root,
        "quality": slot.quality,
        "pitch_class_set": sorted(slot.pitch_class_set),
    }


def chord_slot_from_dict(data: dict[str, object]) -> ChordSlot:
    pcs = data.get("pitch_class_set")
    root = int(str(data["root"]))
    quality = str(data.get("quality", ""))
    if isinstance(pcs, list | tuple | set | frozenset):
        pitch_classes = frozenset(int(pc) for pc in pcs)
    else:
        pitch_classes = frozenset((root + i) % 12 for i in QUALITIES[quality])
    return ChordSlot(root=root, quality=quality, pitch_class_set=pitch_classes)


def chord_grid_for_bars(grid: list[ChordSlot], bars: int) -> list[ChordSlot | None]:
    """Cycle `grid` over `bars` bars; an empty grid means "no harmony" for every bar."""
    if not grid:
        return [None] * bars
    return [grid[i % len(grid)] for i in range(bars)]
