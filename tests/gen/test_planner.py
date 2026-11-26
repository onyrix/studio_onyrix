import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.core.harmony import chord_from_roman, chord_symbol, parse_chord
from app.core.model import Key, Mode
from app.gen.planner import SECTION_KINDS, TEMPLATES, RuleBasedPlanner, normalize_kind

planner = RuleBasedPlanner()


@pytest.mark.parametrize("mode", list(Mode))
def test_every_template_parses(mode: Mode) -> None:
    for template in TEMPLATES[mode]:
        for numeral in template.numerals:
            chord_from_roman(numeral, Key(0, mode))


@given(
    st.builds(Key, st.integers(0, 11), st.sampled_from(list(Mode))),
    st.sampled_from([*SECTION_KINDS, "", "unknown"]),
    st.sampled_from(["", "pop", "jazz", "rock", "nonsense"]),
    st.integers(1, 32),
    st.integers(1, 8),
)
def test_suggestions_have_section_length_and_are_unique(
    key: Key, kind: str, genre: str, bars: int, n: int
) -> None:
    out = planner.suggest_progressions(key, genre, kind, bars, n)
    assert 1 <= len(out) <= n
    assert all(len(grid) == bars for grid in out)
    assert len({tuple(grid) for grid in out}) == len(out)


def test_pop_chorus_in_c_starts_with_the_axis_progression() -> None:
    best = planner.suggest_progressions(Key(0, Mode.MAJOR), "pop", "chorus", 4, 3)[0]
    assert [chord_symbol(c) for c in best] == ["C", "G", "Am", "F"]


def test_jazz_prefers_two_five_one() -> None:
    best = planner.suggest_progressions(Key(0, Mode.MAJOR), "jazz", "verse", 4, 1)[0]
    assert [chord_symbol(c) for c in best][:3] in (["Dm", "G", "C"], ["Dm7", "G7", "Cmaj7"])


def test_progressions_are_transposed_to_the_key() -> None:
    a_minor = planner.suggest_progressions(Key(9, Mode.MINOR), "rock", "verse", 4, 1)[0]
    assert a_minor[0] == parse_chord("Am")


def test_cadences_at_section_end() -> None:
    key = Key(0, Mode.MAJOR)
    for grid in planner.suggest_progressions(key, "pop", "outro", 8, 5):
        assert grid[-1] == parse_chord("C")
    for grid in planner.suggest_progressions(key, "pop", "prechorus", 8, 5):
        assert grid[-1] == parse_chord("G")


def test_deterministic() -> None:
    args = (Key(2, Mode.MINOR), "pop", "verse", 8, 5)
    assert planner.suggest_progressions(*args) == planner.suggest_progressions(*args)


def test_kind_aliases() -> None:
    assert normalize_kind("Pre-Chorus") == "prechorus"
    assert normalize_kind("ritornello") == "chorus"
    assert normalize_kind("Strofa") == "verse"
