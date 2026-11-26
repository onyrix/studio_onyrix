"""Harmony helpers for the chord lane: diatonic chords, progressions and chord change ideas."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import DbSession, get_or_404
from app.api.schemas import MAX_SECTION_BARS
from app.core.harmony import (
    chord_slot_to_dict,
    chord_symbol,
    diatonic_chords,
    parse_chord,
    roman_numeral,
    suggest_next,
)
from app.core.model import ChordSlot, Key, Mode
from app.db.models import Project, Section
from app.gen.planner import SECTION_KINDS, RuleBasedPlanner, kind_from_name, normalize_kind

router = APIRouter(prefix="/harmony", tags=["harmony"])

planner = RuleBasedPlanner()


class ChordOut(BaseModel):
    symbol: str
    numeral: str
    root: int
    quality: str
    pitch_class_set: list[int]


class ProgressionOut(BaseModel):
    chords: list[ChordOut]
    numerals: str


class SuggestRequest(BaseModel):
    project_id: int
    section_id: int | None = None
    section_kind: str | None = None  # default: guessed from the section name
    bars: int | None = Field(default=None, ge=1, le=MAX_SECTION_BARS)
    n: int = Field(default=5, ge=1, le=12)


class SuggestOut(BaseModel):
    section_kind: str
    progressions: list[ProgressionOut]


class NextRequest(BaseModel):
    project_id: int
    chord: str


class NextChordOut(ChordOut):
    kind: str


def chord_out(chord: ChordSlot, key: Key) -> dict[str, Any]:
    return {
        **chord_slot_to_dict(chord),
        "symbol": chord_symbol(chord, key),
        "numeral": roman_numeral(chord, key),
    }


def project_key(project: Project) -> Key:
    return Key(project.key_tonic, Mode(project.key_mode))


@router.get("/diatonic", response_model=list[ChordOut])
def diatonic(
    tonic: int = Query(ge=0, le=11), mode: Mode = Mode.MAJOR, sevenths: bool = False
) -> list[dict[str, Any]]:
    key = Key(tonic, mode)
    return [chord_out(c, key) for c in diatonic_chords(key, sevenths)]


@router.post("/suggest", response_model=SuggestOut)
def suggest(body: SuggestRequest, db: DbSession) -> dict[str, Any]:
    project = get_or_404(db, Project, body.project_id)
    section = None
    if body.section_id is not None:
        section = get_or_404(db, Section, body.section_id)
        if section.project_id != project.id:
            raise HTTPException(422, "section belongs to another project")
    if body.section_kind is not None:
        kind = normalize_kind(body.section_kind)
        if kind and kind not in SECTION_KINDS:
            raise HTTPException(422, f"section_kind must be one of {', '.join(SECTION_KINDS)}")
    else:
        kind = kind_from_name(section.name) if section else ""
    bars = body.bars or (section.bars if section else 4)
    key = project_key(project)
    grids = planner.suggest_progressions(key, project.genre, kind, bars, body.n)
    return {
        "section_kind": kind,
        "progressions": [
            {
                "chords": [chord_out(c, key) for c in grid],
                "numerals": " ".join(roman_numeral(c, key) for c in grid),
            }
            for grid in grids
        ],
    }


@router.post("/next", response_model=list[NextChordOut])
def next_chords(body: NextRequest, db: DbSession) -> list[dict[str, Any]]:
    project = get_or_404(db, Project, body.project_id)
    try:
        prev = parse_chord(body.chord)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    key = project_key(project)
    return [{**chord_out(s.chord, key), "kind": s.kind} for s in suggest_next(prev, key)]
