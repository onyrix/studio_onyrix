"""Reading Chordonomicon-style chord data into key-relative roman numerals (B-57). Pure.

Source format (one song per CSV row): `<intro_1> C <verse_1> F C E7 Amin ... <chorus_1> ...`.
Chord tokens: root `A`..`G`, `s` = sharp (but `Esus4` is E + sus4), `b` = flat, then a quality
(`min`, `7`, `maj7`, `min7`, `no3d` power chord, `sus4`, `add9`, ...) and an optional `/bass`.
Durations are not in the data: chords are a sequence, consecutive repeats carry no meaning.

The song key is not given either: `estimate_key` picks the major/minor key whose scale best
contains the chords, with a bonus for the tonic chord (and for starting / ending on it). Chords
are then reduced to a small numeral vocabulary (`I`, `vi`, `V7`, `bVII`, `ii°`, `III+`) so that
statistics over hundreds of thousands of songs stay dense.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from app.core.harmony import NOTE_TO_PC, NUMERALS, SCALES
from app.core.model import Key, Mode

# Section tags kept for statistics (others, e.g. solo / interlude / instrumental, are skipped).
TAG_KINDS = {
    "intro": "intro",
    "verse": "verse",
    "prechorus": "prechorus",
    "pre-chorus": "prechorus",
    "chorus": "chorus",
    "bridge": "bridge",
    "outro": "outro",
}

# Corpus main genres -> the genre labels the project uses (prism's genre list where possible).
GENRES = {
    "pop": "pop",
    "rock": "rock",
    "pop rock": "rock",
    "alternative": "rock",
    "country": "country",
    "punk": "punk",
    "rap": "hip-hop",
    "metal": "metal",
    "jazz": "jazz",
    "soul": "soul",
    "electronic": "dance-electronic",
    "reggae": "reggae",
}

_TOKEN_RE = re.compile(r"^([A-G])(s(?!us)|b)?([^/]*)(?:/.*)?$")

# Reduced chord families: major, minor, dominant seventh, diminished, augmented, power chord.
MAJOR, MINOR, DOMINANT, DIM, AUG, POWER = "", "m", "7", "dim", "aug", "5"
_FAMILY_INTERVALS = {
    MAJOR: (0, 4, 7),
    MINOR: (0, 3, 7),
    DOMINANT: (0, 4, 7, 10),
    DIM: (0, 3, 6),
    AUG: (0, 4, 8),
    POWER: (0, 7),
}


@dataclass(frozen=True)
class CorpusChord:
    root: int
    family: str  # one of the families above

    @property
    def pitch_classes(self) -> frozenset[int]:
        return frozenset((self.root + i) % 12 for i in _FAMILY_INTERVALS[self.family])


def _family(quality: str) -> str:
    q = quality.lower()
    if q.startswith("no3"):
        return POWER
    if q.startswith("dim"):
        return DIM
    if q.startswith("aug"):
        return AUG
    if q.startswith("min") or q == "mi" or q == "m":
        return MINOR
    if q.startswith("maj") or q.startswith("add") or q.startswith("us") or q.startswith("sus"):
        return MAJOR
    if q[:1].isdigit():
        return DOMINANT  # 7, 9, 11, 13, 7sus4, 7b9 ...
    return MAJOR


def parse_corpus_chord(token: str) -> CorpusChord | None:
    """One chord token (`Csmin`, `Esus4`, `A/Cs`, `Bbmaj7`, `Gno3d`), or None if unreadable."""
    match = _TOKEN_RE.match(token)
    if not match:
        return None
    letter, accidental, quality = match.groups()
    root = NOTE_TO_PC[letter] + {"s": 1, "b": -1}.get(accidental or "", 0)
    return CorpusChord(root % 12, _family(quality))


def parse_song(chords_field: str) -> list[tuple[str, list[CorpusChord]]]:
    """Sections in order as (kind, chords); consecutive repeats are merged, unknown tags and
    unreadable chords are skipped. Kind "" = chords before any tag."""
    sections: list[tuple[str, list[CorpusChord]]] = []
    kind: str | None = ""
    current: list[CorpusChord] = []

    def close() -> None:
        if kind is not None and current:
            sections.append((kind, list(current)))

    for token in chords_field.split():
        if token.startswith("<"):
            close()
            current = []
            tag = re.sub(r"_\d+>?$", "", token.strip("<>")).lower()
            kind = TAG_KINDS.get(tag)
            continue
        chord = parse_corpus_chord(token)
        if chord is not None and (not current or current[-1] != chord):
            current.append(chord)
    close()
    return sections


def estimate_key(chords: Sequence[CorpusChord]) -> Key | None:
    """The major or minor key that best explains the chords (None for no chords).

    Score per key: for every chord, the share of its pitch classes inside the scale; +0.5 for each
    tonic chord of the right family (I in major, i in minor); +2 if the song starts on it and +2
    if it ends on it. Ties prefer major and the lower tonic (deterministic).
    """
    if not chords:
        return None
    counts = Counter(chords)
    best: tuple[float, Key] | None = None
    for mode in (Mode.MAJOR, Mode.MINOR):
        tonic_family = MAJOR if mode is Mode.MAJOR else MINOR
        for tonic in range(12):
            scale = frozenset((tonic + i) % 12 for i in SCALES[mode])
            score = 0.0
            for chord, n in counts.items():
                pcs = chord.pitch_classes
                score += n * len(pcs & scale) / len(pcs)
                if chord.root == tonic and chord.family in (tonic_family, POWER):
                    score += 0.5 * n
            for edge in (chords[0], chords[-1]):
                if edge.root == tonic and edge.family in (tonic_family, POWER):
                    score += 2
            if best is None or score > best[0] + 1e-9:
                best = (score, Key(tonic, mode))
    return best[1] if best else None


def family_of_quality(quality: str) -> str:
    """Reduced family of one of our chord qualities (`core.harmony.QUALITIES`)."""
    if quality in ("dim", "dim7", "m7b5"):
        return DIM
    if quality == "aug":
        return AUG
    if quality in ("7", "9"):
        return DOMINANT
    if quality.startswith("m") and not quality.startswith("maj"):
        return MINOR
    return MAJOR


def numeral(chord: CorpusChord, key: Key) -> str:
    """Reduced roman numeral relative to the key's own scale (natural minor), matching
    `harmony.roman_numeral` conventions: `I`, `vi`, `V7`, `bVII`, `ii°`, `III+`. A power chord
    takes the third the scale implies on its degree."""
    scale = [(key.tonic + i) % 12 for i in SCALES[key.mode]]
    upper = (chord.root + 1) % 12
    if chord.root in scale:
        accidental, degree = "", scale.index(chord.root)
    elif upper in scale and scale.index(upper) != 0:
        accidental, degree = "b", scale.index(upper)
    else:
        accidental, degree = "#", scale.index((chord.root - 1) % 12)
    family = chord.family
    if family == POWER:
        third_major = (chord.root + 4) % 12 in scale
        family = MAJOR if third_major or accidental else MINOR
    name = NUMERALS[degree]
    if family == MINOR:
        return f"{accidental}{name.lower()}"
    if family == DIM:
        return f"{accidental}{name.lower()}°"
    if family == AUG:
        return f"{accidental}{name}+"
    if family == DOMINANT:
        return f"{accidental}{name}7"
    return f"{accidental}{name}"
