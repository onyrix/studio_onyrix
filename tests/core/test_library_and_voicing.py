import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.core import library
from app.core.harmony import chord_symbol, parse_chord
from app.core.model import Key, Mode
from app.core.progression import chord_timeline, parse_progression
from app.core.timebase import TimeSignature
from app.core.voicing import UPPER_HIGH, UPPER_LOW, voice_progression

keys = st.builds(Key, st.integers(0, 11), st.sampled_from(list(Mode)))


@pytest.mark.parametrize("entry", library.PROGRESSIONS, ids=lambda p: p.id)
def test_every_progression_parses_and_is_tagged(entry: library.LibraryProgression) -> None:
    assert library.realize(entry.numerals, Key(0, entry.mode))
    assert entry.moods <= set(library.MOODS)
    assert entry.kinds <= set(library.PART_ORDER)
    assert 0 <= entry.energy <= 1


@pytest.mark.parametrize("kit", library.KITS, ids=lambda k: k.id)
def test_every_kit_parses_and_has_the_core_parts(kit: library.SongKit) -> None:
    assert {"verse", "chorus"} <= set(kit.parts) <= set(library.PART_ORDER)
    assert kit.moods <= set(library.MOODS)
    for numerals in kit.parts.values():
        assert library.realize(numerals, Key(9, kit.mode))


def test_ids_are_unique() -> None:
    assert len({p.id for p in library.PROGRESSIONS}) == len(library.PROGRESSIONS)
    assert len({k.id for k in library.KITS}) == len(library.KITS)


def test_realize_in_a_key() -> None:
    events = library.realize("ii7 V7 Imaj7*2", Key(5, Mode.MAJOR))
    assert [chord_symbol(e.chord, Key(5, Mode.MAJOR)) for e in events] == ["Gm7", "C7", "Fmaj7"]
    assert [e.beats for e in events] == [None, None, 8]
    assert library.length_beats("i (VI VII)", TimeSignature(4, 4)) == 8


def test_search_filters_by_mode_and_mood_and_ranks_by_kind() -> None:
    found = library.search(Mode.MAJOR, kind="prechorus", moods=["tense"])
    assert found and all(p.mode is Mode.MAJOR and "tense" in p.moods for p in found)
    assert "prechorus" in found[0].kinds
    minor = library.search(Mode.MINOR, kind="chorus", genre="rock")
    assert minor[0].id == "minor_epic"


def test_search_prefers_progressions_that_fit_the_section() -> None:
    four_bars = library.search(Mode.MAJOR, kind="verse", bars=4)
    assert library.length_beats(four_bars[0].numerals) <= 16


def test_kits_filter() -> None:
    dark = library.kits(Mode.MINOR, moods=["dark"])
    assert dark and all(k.mode is Mode.MINOR and "dark" in k.moods for k in dark)
    assert len(library.kits()) == len(library.KITS)


def test_voicing_moves_smoothly_and_stays_in_range() -> None:
    spans = chord_timeline(parse_progression("C Am F G"), 4)
    notes = voice_progression(spans)
    upper = [n for n in notes if n.p >= UPPER_LOW]
    assert all(UPPER_LOW <= n.p <= UPPER_HIGH for n in upper)
    by_chord = [sorted(n.p for n in upper if n.t == s.start) for s in spans]
    for chord, span in zip(by_chord, spans, strict=True):
        assert {p % 12 for p in chord} == span.chord.pitch_class_set
    pairs = zip(by_chord, by_chord[1:], strict=False)
    moves = [sum(abs(a - b) for a, b in zip(x, y, strict=True)) for x, y in pairs]
    assert max(moves) <= 6  # voice leading: common tones held, others move by step
    bass = [n.p for n in notes if n.p < UPPER_LOW]
    assert [p % 12 for p in bass] == [0, 9, 5, 7]


@given(keys, st.sampled_from(library.PROGRESSIONS))
def test_every_library_progression_can_be_voiced(
    key: Key, entry: library.LibraryProgression
) -> None:
    key = Key(key.tonic, entry.mode)
    spans = chord_timeline(library.realize(entry.numerals, key), 8)
    notes = voice_progression(spans)
    assert {n.t for n in notes} == {s.start for s in spans}


def test_big_chords_drop_the_fifth() -> None:
    spans = chord_timeline([*parse_progression("Cmaj9")], 1)
    upper = {n.p % 12 for n in voice_progression(spans, bass=False)}
    assert upper == parse_chord("Cmaj9").pitch_class_set - {7}
