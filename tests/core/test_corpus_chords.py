import pytest

from app.core.corpus_chords import (
    DOMINANT,
    MAJOR,
    MINOR,
    POWER,
    CorpusChord,
    estimate_key,
    numeral,
    parse_corpus_chord,
    parse_song,
)
from app.core.harmony import chord_from_roman
from app.core.model import Key, Mode


@pytest.mark.parametrize(
    ("token", "root", "family"),
    [
        ("C", 0, MAJOR),
        ("Csmin", 1, MINOR),
        ("Esus4", 4, MAJOR),  # E + sus4, not E#
        ("Esus2", 4, MAJOR),
        ("Fs7", 6, DOMINANT),
        ("A/Cs", 9, MAJOR),
        ("Bbmaj7", 10, MAJOR),
        ("Gno3d", 7, POWER),
        ("Dmin7", 2, MINOR),
        ("Bdim7", 11, "dim"),
        ("Caug", 0, "aug"),
        ("G13b9", 7, DOMINANT),
        ("Aminmaj7", 9, MINOR),
    ],
)
def test_parse_corpus_chord(token: str, root: int, family: str) -> None:
    assert parse_corpus_chord(token) == CorpusChord(root, family)


@pytest.mark.parametrize("bad", ["H", "x7", "", "<verse_1>"])
def test_parse_corpus_chord_rejects(bad: str) -> None:
    assert parse_corpus_chord(bad) is None


def test_parse_song_sections_and_repeats() -> None:
    song = "<intro_1> C C <verse_1> F C E7 E7 Amin <solo_1> D <chorus_2> G D G"
    sections = parse_song(song)
    assert [(kind, len(chords)) for kind, chords in sections] == [
        ("intro", 1),
        ("verse", 4),
        ("chorus", 3),
    ]
    assert parse_song("C G Amin F")[0][0] == ""  # untagged chords


@pytest.mark.parametrize(
    ("chords", "key"),
    [
        ("C G Amin F C G Amin F C", Key(0, Mode.MAJOR)),
        ("Amin F C G Amin F C G Amin", Key(9, Mode.MINOR)),
        ("E D A/Cs E D A/Cs E", Key(4, Mode.MAJOR)),  # mixolydian rock stays in E
        ("Dmin Bb C Dmin Bb A7 Dmin", Key(2, Mode.MINOR)),  # harmonic V7
        ("Gno3d F C Gno3d", Key(7, Mode.MAJOR)),
    ],
)
def test_estimate_key(chords: str, key: Key) -> None:
    song = [c for c in (parse_corpus_chord(t) for t in chords.split()) if c is not None]
    assert estimate_key(song) == key


def test_estimate_key_of_nothing() -> None:
    assert estimate_key([]) is None


@pytest.mark.parametrize(
    ("token", "key", "expected"),
    [
        ("Amin", Key(0, Mode.MAJOR), "vi"),
        ("G7", Key(0, Mode.MAJOR), "V7"),
        ("Bb", Key(0, Mode.MAJOR), "bVII"),
        ("Bdim", Key(0, Mode.MAJOR), "vii°"),
        ("E", Key(9, Mode.MINOR), "V"),
        ("F", Key(9, Mode.MINOR), "VI"),
        ("Gsdim", Key(9, Mode.MINOR), "#vii°"),
        ("Dno3d", Key(9, Mode.MINOR), "iv"),  # power chord takes the scale's third
        ("Ebno3d", Key(0, Mode.MAJOR), "bIII"),
    ],
)
def test_numeral(token: str, key: Key, expected: str) -> None:
    chord = parse_corpus_chord(token)
    assert chord is not None
    assert numeral(chord, key) == expected


def test_numerals_are_readable_by_chord_from_roman() -> None:
    for token in ("C", "Dmin", "Edim", "G7", "Bb", "Ab", "Fmin", "Eaug"):
        chord = parse_corpus_chord(token)
        assert chord is not None
        chord_from_roman(numeral(chord, Key(0, Mode.MAJOR)), Key(0, Mode.MAJOR))
