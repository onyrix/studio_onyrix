from hypothesis import given
from hypothesis import strategies as st

from app.core import library
from app.core.harmony import chord_symbol, parse_chord
from app.core.model import Key, Mode
from app.gen.planner import SECTION_KINDS, RuleBasedPlanner, kind_from_name, normalize_kind

planner = RuleBasedPlanner()


@given(
    st.builds(Key, st.integers(0, 11), st.sampled_from(list(Mode))),
    st.sampled_from([*SECTION_KINDS, "", "unknown"]),
    st.sampled_from(["", "pop", "jazz", "rock", "nonsense"]),
    st.integers(1, 32),
    st.integers(1, 8),
)
def test_suggestions_are_unique_progressions_of_the_key_mode(
    key: Key, kind: str, genre: str, bars: int, n: int
) -> None:
    out = planner.suggest_progressions(key, genre, kind, bars, n)
    assert 1 <= len(out) <= n
    assert all(s.source.mode is key.mode and s.events for s in out)
    assert len({s.source.id for s in out}) == len(out)


def test_pop_chorus_in_c_starts_with_the_axis_progression() -> None:
    best = planner.suggest_progressions(Key(0, Mode.MAJOR), "pop", "chorus", 4, 3)[0]
    assert [chord_symbol(e.chord) for e in best.events] == ["C", "G", "Am", "F"]


def test_jazz_prefers_two_five_one() -> None:
    best = planner.suggest_progressions(Key(0, Mode.MAJOR), "jazz", "verse", 4, 1)[0]
    assert [chord_symbol(e.chord) for e in best.events] == ["Dm7", "G7", "Cmaj7"]


def test_progressions_are_transposed_to_the_key() -> None:
    a_minor = planner.suggest_progressions(Key(9, Mode.MINOR), "rock", "verse", 4, 1)[0]
    assert a_minor.events[0].chord == parse_chord("Am")


def test_moods_filter() -> None:
    out = planner.suggest_progressions(Key(0, Mode.MAJOR), "", "", 4, 10, moods=["dreamy"])
    assert out and all("dreamy" in s.source.moods for s in out)


def test_deterministic() -> None:
    args = (Key(2, Mode.MINOR), "pop", "verse", 8, 5)
    assert planner.suggest_progressions(*args) == planner.suggest_progressions(*args)


def test_kind_aliases() -> None:
    assert normalize_kind("Pre-Chorus") == "prechorus"
    assert normalize_kind("ritornello") == "chorus"
    assert normalize_kind("Strofa") == "verse"
    assert set(SECTION_KINDS) == set(library.PART_ORDER)


def test_kind_from_section_name() -> None:
    assert kind_from_name("Chorus 2") == "chorus"
    assert kind_from_name("Strofa A") == "verse"
    assert kind_from_name("Pre-Chorus") == "prechorus"
    assert kind_from_name("Drop") == ""
