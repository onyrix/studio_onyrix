"""Tick / step / bar conversions. All bar math in the project goes through here.

Internal resolution is PPQ = 480; a 16th-note step is 120 ticks; a 4/4 bar is 1920 ticks.
Times are always ticks; seconds exist only transiently for playback.
"""

from __future__ import annotations

from dataclasses import dataclass

PPQ = 480
STEPS_PER_QUARTER = 4
STEP_TICKS = PPQ // STEPS_PER_QUARTER  # 120
US_PER_MINUTE = 60_000_000


@dataclass(frozen=True)
class TimeSignature:
    numerator: int = 4
    denominator: int = 4

    def __post_init__(self) -> None:
        if self.numerator < 1:
            raise ValueError(f"numerator must be >= 1, got {self.numerator}")
        if self.denominator not in (1, 2, 4, 8, 16):
            raise ValueError(f"denominator must be a power of two <= 16, got {self.denominator}")


FOUR_FOUR = TimeSignature(4, 4)


def bar_ticks(ts: TimeSignature = FOUR_FOUR) -> int:
    """Length of one bar in ticks."""
    return ts.numerator * PPQ * 4 // ts.denominator


def steps_per_bar(ts: TimeSignature = FOUR_FOUR) -> int:
    return bar_ticks(ts) // STEP_TICKS


def steps_to_ticks(steps: int) -> int:
    return steps * STEP_TICKS


def ticks_to_steps(ticks: int) -> int:
    """Whole steps contained in `ticks` (floor)."""
    return ticks // STEP_TICKS


def bars_to_ticks(bars: int, ts: TimeSignature = FOUR_FOUR) -> int:
    return bars * bar_ticks(ts)


def ticks_to_bars(ticks: int, ts: TimeSignature = FOUR_FOUR) -> int:
    """Index of the bar containing `ticks` (floor)."""
    return ticks // bar_ticks(ts)


def bar_start(bar: int, ts: TimeSignature = FOUR_FOUR) -> int:
    return bars_to_ticks(bar, ts)


def step_in_bar(ticks: int, ts: TimeSignature = FOUR_FOUR) -> int:
    """Step index (0-based) of `ticks` within its bar."""
    return ticks_to_steps(ticks % bar_ticks(ts))


def snap_to_step(ticks: int) -> int:
    """Round to the nearest 16th-note step (ties round up)."""
    return ((ticks + STEP_TICKS // 2) // STEP_TICKS) * STEP_TICKS


def bpm_to_us_per_quarter(bpm: float) -> int:
    if bpm <= 0:
        raise ValueError(f"bpm must be > 0, got {bpm}")
    return round(US_PER_MINUTE / bpm)


def us_per_quarter_to_bpm(us_per_quarter: int) -> float:
    if us_per_quarter <= 0:
        raise ValueError(f"us_per_quarter must be > 0, got {us_per_quarter}")
    return US_PER_MINUTE / us_per_quarter


def ticks_to_seconds(ticks: int, bpm: float) -> float:
    """Playback-only conversion at a constant tempo. Never store the result."""
    if bpm <= 0:
        raise ValueError(f"bpm must be > 0, got {bpm}")
    return ticks / PPQ * 60.0 / bpm
