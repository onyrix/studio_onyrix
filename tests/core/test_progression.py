import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.core.harmony import QUALITIES, make_chord, parse_chord
from app.core.model import Key, Mode
from app.core.progression import (
    ChordEvent,
    ChordSpan,
    bar_spans,
    chord_at,
    chord_timeline,
    chords_in_bar,
    event_from_dict,
    event_to_dict,
    parse_progression,
    progression_text,
)
from app.core.timebase import TimeSignature

C, F, G, AM = (parse_chord(s) for s in ("C", "F", "G", "Am"))
THREE_FOUR = TimeSignature(3, 4)


def test_parse_one_chord_per_bar_is_backward_compatible() -> None:
    assert parse_progression("Am F C G") == [ChordEvent(c) for c in (AM, F, C, G)]
    assert parse_progression("| Am | F, C |") == [ChordEvent(c) for c in (AM, F, C)]


def test_parse_durations_groups_and_repeats() -> None:
    events = parse_progression("C*2 (Am F) G:3 G7:1 %")
    assert events == [
        ChordEvent(C, 8),
        ChordEvent(AM, 2),
        ChordEvent(F, 2),
        ChordEvent(G, 3),
        ChordEvent(parse_chord("G7"), 1),
        ChordEvent(parse_chord("G7")),
    ]


def test_parse_respects_the_time_signature() -> None:
    assert parse_progression("(C F G)", THREE_FOUR) == [ChordEvent(c, 1) for c in (C, F, G)]
    assert parse_progression("C*2", THREE_FOUR) == [ChordEvent(C, 6)]
    with pytest.raises(ValueError, match="evenly"):
        parse_progression("(C F)", THREE_FOUR)


@pytest.mark.parametrize(
    "bad", ["(C (F))", "()", "C)", "(C F", "%", "(C*2 F)", "H7", "C:0", "C:99"]
)
def test_parse_rejects(bad: str) -> None:
    with pytest.raises(ValueError):
        parse_progression(bad)


events_strategy = st.lists(
    st.builds(
        ChordEvent,
        st.builds(make_chord, st.integers(0, 11), st.sampled_from(sorted(QUALITIES))),
        st.sampled_from([None, 1, 2, 3, 4, 6, 8, 12]),
    ),
    max_size=12,
)


@given(events_strategy)
def test_text_round_trip(events: list[ChordEvent]) -> None:
    key = Key(5, Mode.MAJOR)
    assert parse_progression(progression_text(events, key)) == [
        ChordEvent(e.chord, None if e.beats == 4 else e.beats) for e in events
    ]


@given(events_strategy)
def test_dict_round_trip(events: list[ChordEvent]) -> None:
    assert [event_from_dict(event_to_dict(e)) for e in events] == events


def test_progression_text_canonical_form() -> None:
    assert progression_text(parse_progression("C:8 Am:2 F:2 G:3")) == "C*2 (Am F) G:3"


def test_timeline_cycles_and_cuts_at_the_section_end() -> None:
    spans = chord_timeline(parse_progression("C*2 (Am F)"), bars=4)
    assert spans == (
        ChordSpan(0, 3840, C),
        ChordSpan(3840, 4800, AM),
        ChordSpan(4800, 5760, F),
        ChordSpan(5760, 7680, C),  # cycled, cut at bar 4
    )
    assert chord_timeline([], 4) == ()
    assert chord_at(spans, 4799) == AM
    assert chord_at(spans, 7680) is None
    assert chords_in_bar(spans, 2, TimeSignature(4, 4)) == [AM, F]


@given(events_strategy.filter(bool), st.integers(1, 16))
def test_timeline_covers_the_section_without_gaps(events: list[ChordEvent], bars: int) -> None:
    spans = chord_timeline(events, bars)
    assert spans[0].start == 0
    assert spans[-1].end == bars * 1920
    assert all(a.end == b.start for a, b in zip(spans, spans[1:], strict=False))
    assert all(s.start < s.end for s in spans)


def test_bar_spans_skip_bars_without_harmony() -> None:
    assert bar_spans([C, None, G]) == (ChordSpan(0, 1920, C), ChordSpan(3840, 5760, G))
