"""Chord naming, diatonic harmony, roman numerals and chord change suggestions."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.core.harmony import (
    QUALITIES,
    Suggestion,
    chord_from_roman,
    chord_symbol,
    diatonic_chords,
    make_chord,
    parse_chord,
    roman_numeral,
    scale_pitch_classes,
    suggest_next,
)
from app.core.model import Key, Mode

keys = st.builds(Key, st.integers(0, 11), st.sampled_from(list(Mode)))


@given(st.integers(0, 11), st.sampled_from(sorted(QUALITIES)), keys)
def test_chord_symbol_round_trips_through_parse(root: int, quality: str, key: Key) -> None:
    chord = make_chord(root, quality)
    assert parse_chord(chord_symbol(chord, key)) == chord


@pytest.mark.parametrize("symbol", ["C/E", "Am/G", "F#m7b5", "Bbmaj7"])
def test_chord_symbol_keeps_slash_bass(symbol: str) -> None:
    flats = Key(5, Mode.MAJOR)
    assert parse_chord(chord_symbol(parse_chord(symbol), flats)) == parse_chord(symbol)


def test_chord_symbol_spells_by_key() -> None:
    chord = make_chord(10, "")
    assert chord_symbol(chord, Key(5, Mode.MAJOR)) == "Bb"
    assert chord_symbol(chord, Key(11, Mode.MAJOR)) == "A#"
    assert chord_symbol(make_chord(3, "m"), Key(0, Mode.MINOR)) == "Ebm"


def test_out_of_key_roots_are_spelled_by_degree() -> None:
    a_minor, c_major = Key(9, Mode.MINOR), Key(0, Mode.MAJOR)
    assert chord_symbol(make_chord(10, ""), a_minor) == "Bb"  # bII, neapolitan
    assert chord_symbol(make_chord(10, ""), c_major) == "Bb"  # bVII
    assert chord_symbol(make_chord(8, "dim"), a_minor) == "G#dim"  # #vii°


def test_diatonic_triads() -> None:
    names = [chord_symbol(c) for c in diatonic_chords(Key(0, Mode.MAJOR))]
    assert names == ["C", "Dm", "Em", "F", "G", "Am", "Bdim"]
    names = [chord_symbol(c) for c in diatonic_chords(Key(9, Mode.MINOR))]
    assert names == ["Am", "Bdim", "C", "Dm", "Em", "F", "G"]


def test_diatonic_sevenths() -> None:
    names = [chord_symbol(c) for c in diatonic_chords(Key(0, Mode.MAJOR), sevenths=True)]
    assert names == ["Cmaj7", "Dm7", "Em7", "Fmaj7", "G7", "Am7", "Bm7b5"]


@given(keys, st.booleans())
def test_diatonic_chords_stay_in_scale(key: Key, sevenths: bool) -> None:
    scale = scale_pitch_classes(key)
    for chord in diatonic_chords(key, sevenths):
        assert chord.pitch_class_set <= scale


@given(keys, st.booleans())
def test_roman_numerals_round_trip_for_diatonic_chords(key: Key, sevenths: bool) -> None:
    for chord in diatonic_chords(key, sevenths):
        assert chord_from_roman(roman_numeral(chord, key), key) == chord


@pytest.mark.parametrize(
    ("numeral", "key", "symbol"),
    [
        ("V7", Key(0, Mode.MAJOR), "G7"),
        ("bVII", Key(0, Mode.MAJOR), "A#"),
        ("ii", Key(2, Mode.MAJOR), "Em"),
        ("vii°", Key(0, Mode.MAJOR), "Bdim"),
        ("iiø7", Key(9, Mode.MINOR), "Bm7b5"),
        ("VI", Key(9, Mode.MINOR), "F"),
        ("V", Key(9, Mode.MINOR), "E"),
        ("IVmaj7", Key(7, Mode.MAJOR), "Cmaj7"),
    ],
)
def test_chord_from_roman(numeral: str, key: Key, symbol: str) -> None:
    assert chord_from_roman(numeral, key) == parse_chord(symbol)


@pytest.mark.parametrize("bad", ["", "VIII", "Vxyz", "ii°9", "x"])
def test_chord_from_roman_rejects(bad: str) -> None:
    with pytest.raises(ValueError):
        chord_from_roman(bad, Key(0, Mode.MAJOR))


def test_roman_numeral_of_borrowed_chords() -> None:
    c_major = Key(0, Mode.MAJOR)
    assert roman_numeral(parse_chord("Bb"), c_major) == "bVII"
    assert roman_numeral(parse_chord("Ab"), c_major) == "bVI"
    assert roman_numeral(parse_chord("Fm"), c_major) == "iv"
    assert roman_numeral(parse_chord("G#dim"), Key(9, Mode.MINOR)) == "#vii°"


def test_suggest_next_after_tonic_in_major() -> None:
    out = suggest_next(parse_chord("C"), Key(0, Mode.MAJOR))
    functional = [chord_symbol(s.chord) for s in out if s.kind == "functional"]
    assert functional == ["F", "G", "Am", "Dm"]
    kinds = {s.kind for s in out}
    assert {"secondary_dominant", "tritone_sub", "borrowed"} <= kinds
    assert parse_chord("C7") in [s.chord for s in out if s.kind == "secondary_dominant"]


def test_suggest_next_offers_relative_when_not_already_functional() -> None:
    out = suggest_next(parse_chord("Em"), Key(0, Mode.MAJOR))
    assert Suggestion(parse_chord("G"), "relative") in out


def test_suggest_next_minor_uses_major_dominant() -> None:
    out = suggest_next(parse_chord("Dm"), Key(9, Mode.MINOR))
    assert parse_chord("E") in [s.chord for s in out]


@given(keys, st.integers(0, 11), st.sampled_from(["", "m", "7", "dim"]))
def test_suggestions_are_unique_and_differ_from_prev(key: Key, root: int, quality: str) -> None:
    prev = make_chord(root, quality)
    out = suggest_next(prev, key)
    sets = [s.chord.pitch_class_set for s in out]
    assert out
    assert len(sets) == len(set(sets))
    assert prev.pitch_class_set not in sets
