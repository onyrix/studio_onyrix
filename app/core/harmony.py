"""Chord symbols -> pitch class sets, key / scale helpers. Pure."""

from __future__ import annotations

import re
from dataclasses import dataclass

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


# ---- Naming ------------------------------------------------------------------------------

SHARP_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
FLAT_NAMES = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")

# Tonics of the relative major whose key signature uses flats: F Bb Eb Ab Db Gb.
_FLAT_MAJOR_TONICS = frozenset({5, 10, 3, 8, 1, 6})


def relative_major_tonic(key: Key) -> int:
    return key.tonic if key.mode is Mode.MAJOR else (key.tonic + 3) % 12


def prefers_flats(key: Key | None) -> bool:
    return key is not None and relative_major_tonic(key) in _FLAT_MAJOR_TONICS


def pc_name(pc: int, flats: bool = False) -> str:
    return (FLAT_NAMES if flats else SHARP_NAMES)[pc % 12]


def chord_symbol(slot: ChordSlot, key: Key | None = None) -> str:
    """Inverse of `parse_chord`: `Am7`, `Bbmaj7`, `C/E` (one extra pitch class = slash bass)."""
    flats = prefers_flats(key)
    text = pc_name(slot.root, flats) + slot.quality
    base = {(slot.root + i) % 12 for i in QUALITIES.get(slot.quality, ())}
    extra = sorted(slot.pitch_class_set - base)
    if len(extra) == 1:
        text += "/" + pc_name(extra[0], flats)
    return text


def make_chord(root: int, quality: str) -> ChordSlot:
    if quality not in QUALITIES:
        raise ValueError(f"unknown chord quality {quality!r}")
    root %= 12
    return ChordSlot(root, quality, frozenset((root + i) % 12 for i in QUALITIES[quality]))


# ---- Diatonic harmony and roman numerals -------------------------------------------------

_TRIADS: dict[tuple[int, int], str] = {(4, 7): "", (3, 7): "m", (3, 6): "dim", (4, 8): "aug"}
_SEVENTHS: dict[tuple[int, int, int], str] = {
    (4, 7, 11): "maj7",
    (4, 7, 10): "7",
    (3, 7, 10): "m7",
    (3, 6, 10): "m7b5",
    (3, 6, 9): "dim7",
}


def diatonic_chords(key: Key, sevenths: bool = False) -> list[ChordSlot]:
    """The seven chords built in thirds on each degree of the key's scale (natural minor)."""
    scale = [(key.tonic + i) % 12 for i in SCALES[key.mode]]
    out = []
    for degree, root in enumerate(scale):
        third, fifth, seventh = ((scale[(degree + s) % 7] - root) % 12 for s in (2, 4, 6))
        quality = _SEVENTHS[(third, fifth, seventh)] if sevenths else _TRIADS[(third, fifth)]
        out.append(make_chord(root, quality))
    return out


NUMERALS = ("I", "II", "III", "IV", "V", "VI", "VII")
_ROMAN_RE = re.compile(r"^([b#]?)(VII|VI|IV|V|III|II|I|vii|vi|iv|v|iii|ii|i)([°ø+]?)(.*)$")
_UPPER_SUFFIX = frozenset({"", "7", "maj7", "9", "maj9", "6", "sus2", "sus4", "add9"})
_LOWER_SUFFIX = {"": "m", "7": "m7", "9": "m9", "6": "m6"}


def chord_from_roman(numeral: str, key: Key) -> ChordSlot:
    """`V7`, `bVII`, `ii`, `vii°`, `iiø7`, `IVmaj7`, relative to the key's own scale."""
    match = _ROMAN_RE.match(numeral.strip())
    if not match:
        raise ValueError(f"invalid roman numeral: {numeral!r}")
    accidental, letters, mark, suffix = match.groups()
    degree = NUMERALS.index(letters.upper())
    root = key.tonic + SCALES[key.mode][degree] + {"b": -1, "#": 1}.get(accidental, 0)
    quality: str | None
    if mark == "°":
        quality = {"": "dim", "7": "dim7"}.get(suffix)
    elif mark == "ø":
        quality = "m7b5" if suffix in ("", "7") else None
    elif mark == "+":
        quality = "aug" if suffix == "" else None
    elif letters.isupper():
        quality = suffix if suffix in _UPPER_SUFFIX else None
    else:
        quality = _LOWER_SUFFIX.get(suffix)
    if quality is None:
        raise ValueError(f"unsupported chord suffix in {numeral!r}")
    return make_chord(root, quality)


def roman_numeral(slot: ChordSlot, key: Key) -> str:
    """Roman numeral of a chord relative to the key's scale; non-diatonic roots get b or #."""
    scale = [(key.tonic + i) % 12 for i in SCALES[key.mode]]
    upper = (slot.root + 1) % 12
    if slot.root in scale:
        accidental, degree = "", scale.index(slot.root)
    elif upper in scale and scale.index(upper) != 0:
        accidental, degree = "b", scale.index(upper)
    else:
        accidental, degree = "#", scale.index((slot.root - 1) % 12)
    numeral = NUMERALS[degree]
    quality = slot.quality
    if quality in ("dim", "dim7"):
        return f"{accidental}{numeral.lower()}°{'7' if quality == 'dim7' else ''}"
    if quality == "m7b5":
        return f"{accidental}{numeral.lower()}ø7"
    if quality == "aug":
        return f"{accidental}{numeral}+"
    if quality.startswith("m") and not quality.startswith("maj"):
        return f"{accidental}{numeral.lower()}{quality[1:]}"
    return f"{accidental}{numeral}{quality}"


# ---- Chord change suggestions ------------------------------------------------------------

SUGGESTION_KINDS = ("functional", "secondary_dominant", "tritone_sub", "borrowed", "relative")


@dataclass(frozen=True)
class Suggestion:
    chord: ChordSlot
    kind: str  # one of SUGGESTION_KINDS


# Common functional successors per scale degree (0 = tonic), most idiomatic first.
_NEXT: dict[Mode, dict[int, tuple[int, ...]]] = {
    Mode.MAJOR: {
        0: (3, 4, 5, 1),
        1: (4, 6, 3),
        2: (5, 3),
        3: (4, 0, 1),
        4: (0, 5, 3),
        5: (3, 1, 4),
        6: (0, 2),
    },
    Mode.MINOR: {
        0: (5, 3, 6, 4),
        1: (4, 0),
        2: (5, 3, 6),
        3: (4, 6, 0),
        4: (0, 5),
        5: (6, 2, 3),
        6: (2, 0),
    },
}


_BORROWED: dict[Mode, tuple[tuple[int, str], ...]] = {
    Mode.MAJOR: ((5, "m"), (8, ""), (10, "")),
    Mode.MINOR: ((5, ""), (1, "")),
}


def suggest_next(prev: ChordSlot, key: Key) -> list[Suggestion]:
    """Chord changes that sound good after `prev` in `key`, each tagged with the reason.

    Order: functional diatonic moves, the secondary dominant of the most idiomatic next chord,
    a tritone substitute when a dominant is among the next moves, chords borrowed from the
    parallel mode, and the relative major / minor of `prev` as a substitute.
    """
    diatonic = diatonic_chords(key)
    if key.mode is Mode.MINOR:
        diatonic[4] = make_chord(diatonic[4].root, "")  # harmonic minor: major V
    out: list[Suggestion] = []

    def add(chord: ChordSlot, kind: str) -> None:
        if chord.pitch_class_set != prev.pitch_class_set and all(
            s.chord.pitch_class_set != chord.pitch_class_set for s in out
        ):
            out.append(Suggestion(chord, kind))

    scale = [(key.tonic + i) % 12 for i in SCALES[key.mode]]
    degree = scale.index(prev.root) if prev.root in scale else None
    targets = _NEXT[key.mode][degree] if degree is not None else (0, 4)
    for d in targets:
        add(diatonic[d], "functional")
    first = diatonic[targets[0]]
    if first.root != key.tonic:
        add(make_chord(first.root + 7, "7"), "secondary_dominant")
    if 4 in targets:
        add(make_chord(key.tonic + 7 + 6, "7"), "tritone_sub")
    # Major: iv, bVI, bVII. Minor: IV (dorian), bII (neapolitan).
    borrowed = _BORROWED[key.mode]
    for interval, quality in borrowed:
        add(make_chord(key.tonic + interval, quality), "borrowed")
    if prev.quality in ("", "7", "maj7", "6"):
        add(make_chord(prev.root + 9, "m"), "relative")
    elif prev.quality in ("m", "m7", "m6"):
        add(make_chord(prev.root + 3, ""), "relative")
    return out
