import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.core import timebase as tb
from app.core.timebase import FOUR_FOUR, TimeSignature


def test_constants_match_spec() -> None:
    assert tb.PPQ == 480
    assert tb.STEP_TICKS == 120
    assert tb.bar_ticks() == 1920
    assert tb.steps_per_bar() == 16


def test_other_time_signatures() -> None:
    assert tb.bar_ticks(TimeSignature(3, 4)) == 1440
    assert tb.bar_ticks(TimeSignature(6, 8)) == 1440
    assert tb.steps_per_bar(TimeSignature(7, 8)) == 14


@pytest.mark.parametrize("bad", [(0, 4), (4, 3), (4, 32)])
def test_invalid_time_signature(bad: tuple[int, int]) -> None:
    with pytest.raises(ValueError):
        TimeSignature(*bad)


def test_tempo_reference_point() -> None:
    assert tb.bpm_to_us_per_quarter(120) == 500_000
    assert tb.us_per_quarter_to_bpm(500_000) == 120


def test_ticks_to_seconds() -> None:
    assert tb.ticks_to_seconds(tb.bar_ticks(), 120) == pytest.approx(2.0)
    with pytest.raises(ValueError):
        tb.ticks_to_seconds(480, 0)


def test_step_in_bar() -> None:
    assert tb.step_in_bar(0) == 0
    assert tb.step_in_bar(1920 + 4 * 120) == 4
    assert tb.step_in_bar(1919) == 15


@given(st.integers(min_value=0, max_value=10_000))
def test_steps_round_trip(steps: int) -> None:
    assert tb.ticks_to_steps(tb.steps_to_ticks(steps)) == steps


@given(st.integers(min_value=0, max_value=1_000))
def test_bars_round_trip(bars: int) -> None:
    assert tb.ticks_to_bars(tb.bars_to_ticks(bars, FOUR_FOUR)) == bars


@given(st.integers(min_value=0, max_value=1_000_000))
def test_snap_is_on_grid_idempotent_and_close(ticks: int) -> None:
    snapped = tb.snap_to_step(ticks)
    assert snapped % tb.STEP_TICKS == 0
    assert tb.snap_to_step(snapped) == snapped
    assert abs(snapped - ticks) <= tb.STEP_TICKS // 2


@given(st.floats(min_value=20, max_value=400))
def test_tempo_round_trip(bpm: float) -> None:
    back = tb.us_per_quarter_to_bpm(tb.bpm_to_us_per_quarter(bpm))
    assert back == pytest.approx(bpm, rel=1e-4)
