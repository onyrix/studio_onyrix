"""Harmony helpers for the chord lane: diatonic chords, progressions and chord change ideas."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field, field_validator

from app.api.deps import DbSession, get_or_404
from app.api.projects import project_out
from app.api.schemas import MAX_SECTION_BARS, ProjectOut
from app.core import library
from app.core.harmony import (
    chord_slot_to_dict,
    chord_symbol,
    diatonic_chords,
    parse_chord,
    roman_numeral,
    suggest_next,
)
from app.core.library import LibraryProgression
from app.core.model import ChordSlot, Key, Mode
from app.core.progression import (
    ChordEvent,
    chord_timeline,
    event_to_dict,
    parse_progression,
    progression_text,
)
from app.core.timebase import TimeSignature, bar_ticks
from app.core.voicing import voice_progression
from app.db.models import ArrangementItem, Project, Section
from app.gen.planner import SECTION_KINDS, RuleBasedPlanner, kind_from_name, normalize_kind
from app.midi_io import ExportTrack, build_midi, to_bytes

router = APIRouter(prefix="/harmony", tags=["harmony"])

planner = RuleBasedPlanner()


class ChordOut(BaseModel):
    symbol: str
    numeral: str
    root: int
    quality: str
    pitch_class_set: list[int]


class EventOut(ChordOut):
    beats: int  # always explicit here (a whole bar = the time signature numerator)


class ProgressionOut(BaseModel):
    id: str
    chords: list[EventOut]
    chord_text: str  # chord symbols, progression syntax (what a section grid accepts)
    numerals: str  # same rhythm, roman numerals
    moods: list[str]
    energy: float


class SuggestRequest(BaseModel):
    project_id: int
    section_id: int | None = None
    section_kind: str | None = None  # default: guessed from the section name
    bars: int | None = Field(default=None, ge=1, le=MAX_SECTION_BARS)
    moods: list[str] = Field(default_factory=list)
    n: int = Field(default=5, ge=1, le=len(library.PROGRESSIONS))

    @field_validator("moods")
    @classmethod
    def _known_moods(cls, value: list[str]) -> list[str]:
        unknown = sorted(set(value) - set(library.MOODS))
        if unknown:
            raise ValueError(f"unknown moods: {', '.join(unknown)}")
        return value


class SuggestOut(BaseModel):
    section_kind: str
    progressions: list[ProgressionOut]


class NextRequest(BaseModel):
    project_id: int
    chord: str


class NextChordOut(ChordOut):
    kind: str


class ParseRequest(BaseModel):
    project_id: int
    text: str = Field(max_length=4000)


class ParseOut(BaseModel):
    chord_text: str
    events: list[EventOut]


def chord_out(chord: ChordSlot, key: Key) -> dict[str, Any]:
    return {
        **chord_slot_to_dict(chord),
        "symbol": chord_symbol(chord, key),
        "numeral": roman_numeral(chord, key),
    }


def project_key(project: Project) -> Key:
    return Key(project.key_tonic, Mode(project.key_mode))


def project_ts(project: Project) -> TimeSignature:
    return TimeSignature(project.ts_numerator, project.ts_denominator)


def events_out(events: list[ChordEvent], key: Key, ts: TimeSignature) -> list[dict[str, Any]]:
    return [{**chord_out(e.chord, key), "beats": e.beats or ts.numerator} for e in events]


def progression_out(
    source: LibraryProgression, events: list[ChordEvent], key: Key, ts: TimeSignature
) -> dict[str, Any]:
    return {
        "id": source.id,
        "chords": events_out(events, key, ts),
        "chord_text": progression_text(events, key, ts),
        "numerals": progression_text(events, key, ts, namer=lambda c: roman_numeral(c, key)),
        "moods": sorted(source.moods),
        "energy": source.energy,
    }


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
    ts = project_ts(project)
    found = planner.suggest_progressions(key, project.genre, kind, bars, body.n, body.moods, ts)
    return {
        "section_kind": kind,
        "progressions": [progression_out(p.source, p.events, key, ts) for p in found],
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


@router.post("/parse", response_model=ParseOut)
def parse(body: ParseRequest, db: DbSession) -> dict[str, Any]:
    """Validate progression text (core.progression syntax) and return its canonical form."""
    project = get_or_404(db, Project, body.project_id)
    ts = project_ts(project)
    try:
        events = parse_progression(body.text, ts)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    key = project_key(project)
    return {
        "chord_text": progression_text(events, key, ts),
        "events": events_out(events, key, ts),
    }


# ---- Audition ---------------------------------------------------------------------------

AUDITION_PROGRAMS = (0, 33)  # acoustic grand piano, fingered bass


@router.get("/audition.mid")
def audition(
    db: DbSession,
    project_id: int,
    text: str = Query(min_length=1, max_length=4000),
) -> Response:
    """A progression (chord symbols, progression syntax) as block chords with voice leading and
    a root bass, at the project tempo, one pass with loop markers. Played by the browser."""
    project = get_or_404(db, Project, project_id)
    ts = project_ts(project)
    try:
        events = parse_progression(text, ts)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    total = sum(e.length(ts) for e in events)
    bars = -(-total // bar_ticks(ts))
    spans = [s for s in chord_timeline(events, bars, ts) if s.start < total]
    notes = voice_progression(spans)
    upper = tuple(n for n in notes if n.p >= 48)
    bass = tuple(n for n in notes if n.p < 48)
    tracks = [
        ExportTrack("Chords", AUDITION_PROGRAMS[0], False, upper),
        ExportTrack("Bass", AUDITION_PROGRAMS[1], False, bass),
    ]
    mid = build_midi("Audition", project.bpm, ts, tracks, loop_ticks=total)
    return Response(to_bytes(mid), media_type="audio/midi")


# ---- Song kits --------------------------------------------------------------------------


class KitPartOut(BaseModel):
    kind: str
    chord_text: str
    numerals: str
    bars: int  # suggested section length


class KitOut(BaseModel):
    id: str
    moods: list[str]
    genres: list[str]
    parts: list[KitPartOut]


class KitApply(BaseModel):
    project_id: int
    kit_id: str
    create_missing: bool = True
    # Display names for sections the kit creates, by kind (the UI sends translated names).
    names: dict[str, str] = Field(default_factory=dict)


def kit_out(kit: library.SongKit, key: Key, ts: TimeSignature) -> dict[str, Any]:
    parts = []
    for kind in library.PART_ORDER:
        if kind not in kit.parts:
            continue
        events = library.realize(kit.parts[kind], key, ts)
        parts.append(
            {
                "kind": kind,
                "chord_text": progression_text(events, key, ts),
                "numerals": progression_text(
                    events, key, ts, namer=lambda c: roman_numeral(c, key)
                ),
                "bars": kit.bars.get(kind, library.DEFAULT_BARS[kind]),
            }
        )
    return {
        "id": kit.id,
        "moods": sorted(kit.moods),
        "genres": sorted(kit.genres),
        "parts": parts,
    }


@router.get("/kits", response_model=list[KitOut])
def list_kits(
    db: DbSession, project_id: int, moods: Annotated[list[str] | None, Query()] = None
) -> list[dict[str, Any]]:
    """Song kits in the project's mode, realized in its key; best genre / mood match first."""
    project = get_or_404(db, Project, project_id)
    key, ts = project_key(project), project_ts(project)
    found = library.kits(key.mode, project.genre.strip().lower(), moods or ())
    return [kit_out(k, key, ts) for k in found]


# Song form used when a kit fills an empty arrangement: repeated kinds are instances of the same
# section (edit once, change everywhere).
SONG_FORM = (
    "intro",
    "verse",
    "prechorus",
    "chorus",
    "verse",
    "prechorus",
    "chorus",
    "bridge",
    "chorus",
    "outro",
)


@router.post("/kits/apply", response_model=ProjectOut)
def apply_kit(body: KitApply, db: DbSession) -> ProjectOut:
    """Write a kit's parts into the sections of matching kind (by name, e.g. "Chorus 2");
    with `create_missing`, create the missing ones. An empty arrangement gets a full song form.
    Returns the updated project."""
    project = get_or_404(db, Project, body.project_id)
    kit = next((k for k in library.KITS if k.id == body.kit_id), None)
    if kit is None:
        raise HTTPException(404, f"kit {body.kit_id} not found")
    key, ts = project_key(project), project_ts(project)
    by_kind: dict[str, list[Section]] = {}
    for section in project.sections:
        by_kind.setdefault(kind_from_name(section.name), []).append(section)
    created: dict[str, Section] = {}
    for kind, numerals in kit.parts.items():
        grid = [event_to_dict(e) for e in library.realize(numerals, key, ts)]
        targets = by_kind.get(kind, [])
        for section in targets:
            section.chord_grid = grid
        if not targets and body.create_missing:
            section = Section(
                name=body.names.get(kind) or kind.capitalize(),
                bars=kit.bars.get(kind, library.DEFAULT_BARS[kind]),
                chord_grid=grid,
            )
            project.sections.append(section)
            created[kind] = section
    db.flush()
    if created:
        if project.arrangement:
            order = [created[k] for k in library.PART_ORDER if k in created]
        else:
            order = [created[k] for k in SONG_FORM if k in created]
        start = len(project.arrangement)
        for offset, section in enumerate(order):
            project.arrangement.append(
                ArrangementItem(position=start + offset, section_id=section.id)
            )
    db.commit()
    db.refresh(project)
    return project_out(project)
