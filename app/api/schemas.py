"""Pydantic request / response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import MAX_CANDIDATES
from app.core.model import Mode, Role
from app.core.progression import event_from_dict, event_to_dict

MAX_SECTION_BARS = 64

# A chord grid arrives as progression text ("C*2 (Am F) G:3", see core.progression), as a list
# of chord tokens (joined into text), or as a list of stored event dicts
# ({root, quality[, pitch_class_set][, beats]}). Text needs the project's time signature, so it
# is kept as a string here and parsed by the route (`app.api.projects.resolve_grid`).
ChordGridIn = list[dict[str, Any]] | str


def normalize_chord_grid(value: Any) -> Any:
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return " ".join(value)
    if isinstance(value, list):
        return [event_to_dict(event_from_dict(item)) for item in value]
    raise ValueError("chord_grid must be text, a list of chord symbols or a list of chords")


class _ChordGridMixin(BaseModel):
    @field_validator("chord_grid", mode="before", check_fields=False)
    @classmethod
    def _parse_grid(cls, value: Any) -> Any:
        try:
            return normalize_chord_grid(value)
        except (ValueError, KeyError, TypeError) as exc:
            raise ValueError(str(exc)) from exc


class ProjectCreate(_ChordGridMixin):
    name: str = Field(min_length=1, max_length=200)
    bpm: float = Field(default=120.0, gt=20, le=400)
    ts_numerator: int = Field(default=4, ge=1, le=16)
    ts_denominator: int = Field(default=4)
    key_tonic: int = Field(default=0, ge=0, le=11)
    key_mode: Mode = Mode.MAJOR
    genre: str = ""
    chord_grid: ChordGridIn = Field(default_factory=list)

    @field_validator("ts_denominator")
    @classmethod
    def _power_of_two(cls, value: int) -> int:
        if value not in (1, 2, 4, 8, 16):
            raise ValueError("ts_denominator must be 1, 2, 4, 8 or 16")
        return value


class ProjectPatch(_ChordGridMixin):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    bpm: float | None = Field(default=None, gt=20, le=400)
    key_tonic: int | None = Field(default=None, ge=0, le=11)
    key_mode: Mode | None = None
    genre: str | None = None
    chord_grid: ChordGridIn | None = None


class TrackCreate(BaseModel):
    role: Role
    name: str | None = Field(default=None, max_length=200)
    program: int | None = Field(default=None, ge=0, le=127)


class TrackPatch(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    program: int | None = Field(default=None, ge=0, le=127)
    mute: bool | None = None
    solo: bool | None = None


class TrackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Role
    program: int
    name: str
    mute: bool
    solo: bool
    position: int


class SectionCreate(_ChordGridMixin):
    name: str = Field(min_length=1, max_length=200)
    bars: int = Field(ge=1, le=MAX_SECTION_BARS)
    chord_grid: ChordGridIn = Field(default_factory=list)


class SectionPatch(_ChordGridMixin):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    chord_grid: ChordGridIn | None = None


class SectionOut(BaseModel):
    id: int
    name: str
    bars: int
    chord_grid: list[dict[str, Any]]
    chord_text: str
    slots: dict[int, int]  # track_id -> clip_id


class ProjectOut(BaseModel):
    id: int
    name: str
    bpm: float
    ts_numerator: int
    ts_denominator: int
    key_tonic: int
    key_mode: Mode
    genre: str
    chord_grid: list[dict[str, Any]]
    chord_text: str
    tracks: list[TrackOut]
    sections: list[SectionOut]
    arrangement: list[int]  # section ids in order


class ProjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bpm: float
    genre: str


class ArrangementIn(BaseModel):
    section_ids: list[int]


class NoteModel(BaseModel):
    t: int = Field(ge=0)
    p: int = Field(ge=0, le=127)
    d: int = Field(gt=0)
    v: int = Field(ge=1, le=127)


class ClipVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seed: int | None
    source: str
    score: float | None
    params: dict[str, Any]
    notes: list[NoteModel]
    created_at: datetime


class ClipOut(BaseModel):
    id: int
    track_id: int
    bars: int
    locked: bool
    current_version: ClipVersionOut | None


class ClipPatch(BaseModel):
    locked: bool | None = None
    notes: list[NoteModel] | None = None  # a manual edit creates a new version


class GenerateControls(BaseModel):
    density: int | None = Field(default=None, ge=0, le=9)
    harmony: Literal["off", "light", "normal", "strict"] = "normal"
    temperature: float = Field(default=1.0, gt=0, le=2)
    top_p: float = Field(default=0.95, gt=0, le=1)


class GenerateRequest(BaseModel):
    section_id: int
    track_id: int
    bars: int | None = Field(default=None, ge=1, le=MAX_SECTION_BARS)
    controls: GenerateControls = Field(default_factory=GenerateControls)
    n_candidates: int | None = Field(default=None, ge=1, le=MAX_CANDIDATES)
    seed: int | None = Field(default=None, ge=0, lt=2**31)


class JobOut(BaseModel):
    id: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None
