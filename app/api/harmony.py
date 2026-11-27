"""Harmony helpers for the chord lane: diatonic chords, progressions and chord change ideas."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request, Response
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
from app.core.harmony_stats import HarmonyStats, numerals_of, surprise_level
from app.core.library import LibraryProgression
from app.core.model import ChordSlot, Key, Mode
from app.core.operators import OPERATORS, NotApplicable, transform
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
from app.gen.llm import OllamaClient
from app.gen.planner import SECTION_KINDS, RuleBasedPlanner, kind_from_name, normalize_kind
from app.gen.prompting import interpret_harmony
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
    surprise: float  # bits per chord change (see core.harmony_stats)
    surprise_level: float  # 0 idiomatic .. 1 very unusual


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
    section_id: int | None = None  # for the surprise of the section's kind


class ParseOut(BaseModel):
    chord_text: str
    numerals: str
    events: list[EventOut]
    surprise: float
    surprise_level: float


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


def stats_of(request: Request) -> HarmonyStats:
    """Corpus statistics when imported, else the library's (`app.corpus.CorpusStore`)."""
    stats: HarmonyStats = request.app.state.corpus.stats()
    return stats


def described(
    events: list[ChordEvent],
    key: Key,
    ts: TimeSignature,
    stats: HarmonyStats,
    kind: str,
    genre: str,
) -> dict[str, Any]:
    """Events as the UI needs them: chords, text, numerals and surprise."""
    bits = stats.surprise(key.mode, kind, genre, numerals_of(events, key))
    return {
        "chords": events_out(events, key, ts),
        "chord_text": progression_text(events, key, ts),
        "numerals": progression_text(events, key, ts, namer=lambda c: roman_numeral(c, key)),
        "surprise": round(bits, 3),
        "surprise_level": round(surprise_level(bits), 3),
    }


def progression_out(
    source: LibraryProgression,
    events: list[ChordEvent],
    key: Key,
    ts: TimeSignature,
    stats: HarmonyStats,
    kind: str,
    genre: str,
) -> dict[str, Any]:
    return {
        "id": source.id,
        **described(events, key, ts, stats, kind, genre),
        "moods": sorted(source.moods),
        "energy": source.energy,
    }


def section_of(db: Any, project: Project, section_id: int | None) -> Section | None:
    if section_id is None:
        return None
    section = get_or_404(db, Section, section_id)
    if section.project_id != project.id:
        raise HTTPException(422, "section belongs to another project")
    return section


def resolve_kind(section_kind: str | None, section: Section | None) -> str:
    if section_kind is not None:
        kind = normalize_kind(section_kind)
        if kind and kind not in SECTION_KINDS:
            raise HTTPException(422, f"section_kind must be one of {', '.join(SECTION_KINDS)}")
        return kind
    return kind_from_name(section.name) if section else ""


@router.get("/diatonic", response_model=list[ChordOut])
def diatonic(
    tonic: int = Query(ge=0, le=11), mode: Mode = Mode.MAJOR, sevenths: bool = False
) -> list[dict[str, Any]]:
    key = Key(tonic, mode)
    return [chord_out(c, key) for c in diatonic_chords(key, sevenths)]


@router.post("/suggest", response_model=SuggestOut)
def suggest(body: SuggestRequest, db: DbSession, request: Request) -> dict[str, Any]:
    project = get_or_404(db, Project, body.project_id)
    section = section_of(db, project, body.section_id)
    kind = resolve_kind(body.section_kind, section)
    bars = body.bars or (section.bars if section else 4)
    key, ts = project_key(project), project_ts(project)
    genre = project.genre.strip().lower()
    stats = stats_of(request)
    found = planner.suggest_progressions(key, project.genre, kind, bars, body.n, body.moods, ts)
    return {
        "section_kind": kind,
        "progressions": [
            progression_out(p.source, p.events, key, ts, stats, kind, genre) for p in found
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


@router.post("/parse", response_model=ParseOut)
def parse(body: ParseRequest, db: DbSession, request: Request) -> dict[str, Any]:
    """Validate progression text (core.progression syntax): canonical form, numerals, surprise."""
    project = get_or_404(db, Project, body.project_id)
    section = section_of(db, project, body.section_id)
    ts = project_ts(project)
    try:
        events = parse_progression(body.text, ts)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    key = project_key(project)
    kind = resolve_kind(None, section)
    out = described(events, key, ts, stats_of(request), kind, project.genre.strip().lower())
    out["events"] = out.pop("chords")
    return out


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


# ---- Explorer: generator and operators --------------------------------------------------


class ExploreRequest(BaseModel):
    project_id: int
    section_id: int | None = None
    section_kind: str | None = None
    length: int = Field(default=4, ge=2, le=16)  # chords, one bar each
    audacity: float = Field(default=0.3, ge=0, le=1)
    seed: int = Field(default=0, ge=0, lt=2**31)
    n: int = Field(default=6, ge=1, le=12)


class ExploredOut(BaseModel):
    chords: list[EventOut]
    chord_text: str
    numerals: str
    surprise: float
    surprise_level: float


class ExploreOut(BaseModel):
    source: str  # "chordonomicon" or "library"
    section_kind: str
    progressions: list[ExploredOut]


@router.post("/explore", response_model=ExploreOut)
def explore(body: ExploreRequest, db: DbSession, request: Request) -> dict[str, Any]:
    """New progressions sampled from the chord statistics; audacity 0 = idiomatic, 1 = unusual
    but attested. Same seed, same ideas."""
    project = get_or_404(db, Project, body.project_id)
    kind = resolve_kind(body.section_kind, section_of(db, project, body.section_id))
    key, ts = project_key(project), project_ts(project)
    genre = project.genre.strip().lower()
    stats = stats_of(request)
    found = stats.generate(key.mode, kind, genre, body.length, body.audacity, body.seed, body.n)
    return {
        "source": stats.source,
        "section_kind": kind,
        "progressions": [
            described(library.realize(" ".join(seq), key, ts), key, ts, stats, kind, genre)
            for seq, _ in found
        ],
    }


class OperatorOut(BaseModel):
    id: str
    scope: str


@router.get("/operators", response_model=list[OperatorOut])
def operators() -> list[dict[str, str]]:
    return [{"id": op.id, "scope": op.scope} for op in OPERATORS.values()]


class TransformRequest(BaseModel):
    project_id: int
    section_id: int | None = None
    text: str = Field(min_length=1, max_length=4000)
    operator: str
    index: int = Field(default=0, ge=0)  # the chord a chord operator acts on


@router.post("/transform", response_model=ExploredOut)
def transform_progression(
    body: TransformRequest, db: DbSession, request: Request
) -> dict[str, Any]:
    """Apply one operator (`GET /harmony/operators`); 422 when it does not apply."""
    project = get_or_404(db, Project, body.project_id)
    kind = resolve_kind(None, section_of(db, project, body.section_id))
    key, ts = project_key(project), project_ts(project)
    if body.operator not in OPERATORS:
        raise HTTPException(404, f"operator {body.operator} not found")
    try:
        events = transform(body.operator, parse_progression(body.text, ts), body.index, key, ts)
    except ValueError as exc:  # NotApplicable is a ValueError
        raise HTTPException(422, str(exc)) from exc
    return described(events, key, ts, stats_of(request), kind, project.genre.strip().lower())


# ---- Prompt ----------------------------------------------------------------------------


class PromptRequest(BaseModel):
    project_id: int
    section_id: int | None = None
    text: str = Field(min_length=1, max_length=1000)
    seed: int = Field(default=0, ge=0, lt=2**31)
    n: int = Field(default=4, ge=1, le=8)  # per origin (library, generated)


class PromptedOut(ExploredOut):
    origin: str  # "library" | "generated"


class PromptOut(BaseModel):
    source: str  # who read the prompt: "ollama" | "keywords"
    intent: dict[str, Any]
    key: dict[str, Any]  # the key the results are in (the project's, or its parallel mode)
    progressions: list[PromptedOut]


def apply_operators(
    events: list[ChordEvent], operators: tuple[str, ...], key: Key, ts: TimeSignature
) -> list[ChordEvent]:
    for operator in operators:
        try:
            events = transform(operator, events, 0, key, ts)
        except NotApplicable:
            continue
    return events


@router.post("/prompt", response_model=PromptOut)
def from_prompt(body: PromptRequest, db: DbSession, request: Request) -> dict[str, Any]:
    """A free-text request -> harmonic parameters (local LLM if available, else keywords) ->
    matching library progressions and generated ideas, with the requested operators applied."""
    project = get_or_404(db, Project, body.project_id)
    section = section_of(db, project, body.section_id)
    client: OllamaClient | None = getattr(request.app.state, "llm", None)
    intent, source = interpret_harmony(body.text, client)
    base = project_key(project)
    key = Key(base.tonic, intent.mode) if intent.mode else base
    ts = project_ts(project)
    kind = intent.kind or resolve_kind(None, section)
    genre = intent.genre or project.genre.strip().lower()
    bars = section.bars if section else 4
    stats = stats_of(request)
    out: list[dict[str, Any]] = []
    found = planner.suggest_progressions(key, genre, kind, bars, body.n, intent.moods, ts)
    if not found:
        found = planner.suggest_progressions(key, genre, kind, bars, body.n, (), ts)
    for p in found:
        events = apply_operators(p.events, intent.operators, key, ts)
        out.append({"origin": "library", **described(events, key, ts, stats, kind, genre)})
    audacity = intent.audacity if intent.audacity is not None else 0.35
    ideas = stats.generate(key.mode, kind, genre, intent.length or 4, audacity, body.seed, body.n)
    for seq, _ in ideas:
        events = apply_operators(library.realize(" ".join(seq), key, ts), intent.operators, key, ts)
        out.append({"origin": "generated", **described(events, key, ts, stats, kind, genre)})
    return {
        "source": source,
        "intent": intent.as_dict(),
        "key": {"tonic": key.tonic, "mode": key.mode.value, "changed": key != base},
        "progressions": out,
    }
