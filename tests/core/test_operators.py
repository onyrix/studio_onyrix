import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.core.harmony import QUALITIES, make_chord
from app.core.model import Key, Mode
from app.core.operators import OPERATORS, NotApplicable, identify_chord, transform
from app.core.progression import ChordEvent, parse_progression, progression_text
from app.core.timebase import TimeSignature

C = Key(0, Mode.MAJOR)
A_MINOR = Key(9, Mode.MINOR)


def run(op: str, text: str, index: int = 0, key: Key = C) -> str:
    return progression_text(transform(op, parse_progression(text), index, key), key)


@pytest.mark.parametrize(
    ("op", "text", "index", "expected"),
    [
        ("relative", "C G Am F", 0, "Am G Am F"),
        ("relative", "C G Am F", 2, "C G C F"),
        ("borrow", "C G Am F", 3, "C G Am Fm"),
        ("borrow", "C G Am F", 2, "C G Ab F"),
        ("tritone_sub", "Dm7 G7 Cmaj7*2", 1, "Dm7 Db7 Cmaj7*2"),
        ("secondary_dominant", "C G Am F", 2, "C (G E7) Am F"),
        ("secondary_dominant", "C:1 Am", 1, "C:1 (E7 Am)"),
        ("chromatic_mediant", "C G Am F", 0, "E G Am F"),
        ("chromatic_mediant", "C G Am F", 2, "C G Fm F"),
        ("sus_resolve", "C G Am F", 1, "C (Gsus4 G) Am F"),
        ("passing_diminished", "C G Am F", 1, "C (G Abdim7) Am F"),
        ("deceptive", "F G C C", 2, "F G Am C"),
        ("sevenths", "C G Am F", 0, "Cmaj7 G7 Am7 Fmaj7"),
        ("tonic_pedal", "C G F", 0, "C G/C F"),
        ("negative_harmony", "C G Am F", 0, "Cm Fm Eb Gm"),
        ("double_time", "C G Am F", 0, "(C G) (Am F)"),
        ("half_time", "C G", 0, "C*2 G*2"),
        ("step_up", "C G Am F", 0, "D A Bm G"),
    ],
)
def test_operators(op: str, text: str, index: int, expected: str) -> None:
    assert run(op, text, index) == expected


def test_minor_key_deceptive_and_borrow() -> None:
    assert run("deceptive", "E Am", 1, A_MINOR) == "E F"
    assert run("borrow", "Am Dm E Am", 1, A_MINOR) == "Am D E Am"


@pytest.mark.parametrize(
    ("op", "text", "index"),
    [
        ("tritone_sub", "Am", 0),
        ("relative", "Bdim", 0),
        ("deceptive", "C G", 1),
        ("sus_resolve", "C:1", 0),
        ("double_time", "C:3", 0),
        ("borrow", "C F# G", 1),
        ("passing_diminished", "C", 0),
        ("sevenths", "C# F#", 0),
        ("relative", "C", 5),
    ],
)
def test_not_applicable(op: str, text: str, index: int) -> None:
    with pytest.raises(NotApplicable):
        transform(op, parse_progression(text), index, C)


def test_unknown_operator() -> None:
    with pytest.raises(KeyError):
        transform("nope", parse_progression("C"), 0, C)


events_strategy = st.lists(
    st.builds(
        ChordEvent,
        st.builds(make_chord, st.integers(0, 11), st.sampled_from(["", "m", "7", "maj7", "m7"])),
        st.sampled_from([None, 2, 4, 8]),
    ),
    min_size=1,
    max_size=8,
)


@given(events_strategy, st.sampled_from(sorted(OPERATORS)), st.integers(0, 7))
def test_operators_keep_length_and_produce_valid_events(
    events: list[ChordEvent], op: str, index: int
) -> None:
    ts = TimeSignature(4, 4)
    try:
        out = transform(op, events, index % len(events), C, ts)
    except NotApplicable:
        return
    length = sum(e.length(ts) for e in events)
    new_length = sum(e.length(ts) for e in out)
    if op == "double_time":
        assert new_length * 2 == length
    elif op == "half_time":
        assert new_length == length * 2
    else:
        assert new_length == length
    assert out


def test_identify_chord() -> None:
    assert identify_chord(make_chord(5, "m6").pitch_class_set, prefer_root=5) == make_chord(5, "m6")
    for quality in ("", "m", "dim", "aug"):
        chord = make_chord(2, quality)
        assert identify_chord(chord.pitch_class_set, prefer_root=2) == chord
    assert identify_chord(frozenset({0, 1, 2})) is None
    assert all(q in QUALITIES for q in ("m6", "7"))
