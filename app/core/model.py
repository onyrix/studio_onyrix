"""Pure domain dataclasses. No I/O, no framework imports."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.core.timebase import FOUR_FOUR, TimeSignature, bars_to_ticks


class Role(str, Enum):
    DRUMS = "drums"
    BASS = "bass"
    CHORDS = "chords"
    PAD = "pad"
    LEAD = "lead"
    OTHER = "other"


class ClipSource(str, Enum):
    MODEL = "model"
    MANUAL = "manual"
    IMPORT = "import"


class Mode(str, Enum):
    MAJOR = "major"
    MINOR = "minor"


@dataclass(frozen=True)
class Note:
    """A note in ticks relative to the clip start: t=start, p=pitch, d=duration, v=velocity."""

    t: int
    p: int
    d: int
    v: int

    def __post_init__(self) -> None:
        if self.t < 0:
            raise ValueError(f"t must be >= 0, got {self.t}")
        if not 0 <= self.p <= 127:
            raise ValueError(f"p must be in 0..127, got {self.p}")
        if self.d <= 0:
            raise ValueError(f"d must be > 0, got {self.d}")
        if not 1 <= self.v <= 127:
            raise ValueError(f"v must be in 1..127, got {self.v}")

    @property
    def end(self) -> int:
        return self.t + self.d

    def to_dict(self) -> dict[str, int]:
        return {"t": self.t, "p": self.p, "d": self.d, "v": self.v}

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> Note:
        return cls(t=int(data["t"]), p=int(data["p"]), d=int(data["d"]), v=int(data["v"]))


@dataclass(frozen=True)
class Key:
    tonic: int  # pitch class 0..11 (C=0)
    mode: Mode = Mode.MAJOR

    def __post_init__(self) -> None:
        if not 0 <= self.tonic <= 11:
            raise ValueError(f"tonic must be a pitch class 0..11, got {self.tonic}")


@dataclass(frozen=True)
class ChordSlot:
    """One bar of the chord grid."""

    root: int  # pitch class 0..11
    quality: str
    pitch_class_set: frozenset[int]

    def __post_init__(self) -> None:
        if not 0 <= self.root <= 11:
            raise ValueError(f"root must be a pitch class 0..11, got {self.root}")
        if any(not 0 <= pc <= 11 for pc in self.pitch_class_set):
            raise ValueError("pitch_class_set must contain pitch classes 0..11")


@dataclass(frozen=True)
class Clip:
    bars: int
    notes: tuple[Note, ...] = ()
    locked: bool = False

    def __post_init__(self) -> None:
        if self.bars < 1:
            raise ValueError(f"bars must be >= 1, got {self.bars}")

    def length_ticks(self, ts: TimeSignature = FOUR_FOUR) -> int:
        return bars_to_ticks(self.bars, ts)


@dataclass
class Section:
    name: str
    bars: int
    slots: dict[int, int] = field(default_factory=dict)  # track_id -> clip_id

    def __post_init__(self) -> None:
        if self.bars < 1:
            raise ValueError(f"bars must be >= 1, got {self.bars}")
