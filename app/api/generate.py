"""Generation endpoints: jobs run on the single worker; progress streams over SSE."""

from __future__ import annotations

import asyncio
import json
import secrets
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import DbSession, EngineDep, JobsDep, SettingsDep, get_or_404
from app.api.schemas import GenerateRequest, JobOut
from app.config import Settings
from app.core.model import ClipSource, Key, Mode, Note, Role
from app.core.progression import chord_timeline, event_from_dict
from app.core.roles import role_spec
from app.core.timebase import TimeSignature
from app.db.models import Clip, ClipVersion, Section, SectionSlot, Track
from app.gen.adapter import ContextTrack, GenerationSpec
from app.gen.engine import ScoredCandidate, generate_candidates
from app.gen.jobs import TERMINAL, Job

router = APIRouter(tags=["generate"])

SEED_LIMIT = 2**31 - 1 - 8  # room for seed + candidate index


@router.get("/models/info")
def models_info(engine: EngineDep) -> dict[str, Any]:
    return engine.info()


def _context_tracks(section: Section, target_track_id: int) -> tuple[ContextTrack, ...]:
    """Every other clip present in the section (locked clips included) as fixed context."""
    out = []
    for slot in section.slots:
        if slot.track_id == target_track_id:
            continue
        clip = slot.clip
        version = clip.current_version
        if version is None or not version.notes:
            continue
        track = clip.track
        out.append(
            ContextTrack(
                track_id=track.id,
                role=Role(track.role),
                program=track.program,
                notes=tuple(Note.from_dict(n) for n in version.notes),
            )
        )
    return tuple(sorted(out, key=lambda c: c.track_id))


def build_spec(
    db: Session, body: GenerateRequest, settings: Settings
) -> tuple[GenerationSpec, Section, Track]:
    section = get_or_404(db, Section, body.section_id)
    track = get_or_404(db, Track, body.track_id)
    project = section.project
    if track.project_id != project.id:
        raise HTTPException(422, "track and section belong to different projects")
    if body.bars is not None and body.bars != section.bars:
        raise HTTPException(422, f"bars must equal the section length ({section.bars})")
    slot = next((s for s in section.slots if s.track_id == track.id), None)
    if slot is not None and slot.clip.locked:
        raise HTTPException(409, "the clip in this slot is locked")

    grid = section.chord_grid or project.chord_grid
    ts = TimeSignature(project.ts_numerator, project.ts_denominator)
    chords = chord_timeline([event_from_dict(c) for c in grid], section.bars, ts)
    role = Role(track.role)
    n = body.n_candidates or settings.n_candidates
    seed = body.seed if body.seed is not None else secrets.randbelow(SEED_LIMIT)
    spec = GenerationSpec(
        bars=section.bars,
        target_role=role,
        target_spec=role_spec(role),
        target_program=track.program,
        context=_context_tracks(section, track.id),
        bpm=project.bpm,
        ts=ts,
        key=Key(project.key_tonic, Mode(project.key_mode)),
        genre=project.genre,
        chords=chords,
        density=body.controls.density,
        n_candidates=n,
        seed=seed,
        temperature=body.controls.temperature,
        top_p=body.controls.top_p,
        harmony=body.controls.harmony,
    )
    return spec, section, track


def save_best(
    db: Session,
    section_id: int,
    track_id: int,
    spec: GenerationSpec,
    ranked: list[ScoredCandidate],
    params: dict[str, Any],
) -> dict[str, Any]:
    valid = [c for c in ranked if c.rejected is None]
    if not valid:
        reasons = sorted({c.rejected or "" for c in ranked})
        raise RuntimeError(f"no valid candidate ({', '.join(reasons)})")
    best = valid[0]
    section = get_or_404(db, Section, section_id)
    slot = next((s for s in section.slots if s.track_id == track_id), None)
    if slot is None:
        clip = Clip(track_id=track_id, bars=section.bars)
        db.add(clip)
        db.flush()
        section.slots.append(SectionSlot(track_id=track_id, clip_id=clip.id))
    else:
        clip = slot.clip
        if clip.locked:
            raise RuntimeError("the clip was locked while generating")
    version = ClipVersion(
        clip=clip,
        notes=[n.to_dict() for n in best.notes],
        seed=best.seed,
        source=ClipSource.MODEL.value,
        score=best.score,
        params={
            **params,
            "request_seed": spec.seed,
            "n_candidates": spec.n_candidates,
            "breakdown": best.breakdown.as_dict() if best.breakdown else None,
        },
    )
    db.add(version)
    db.flush()
    clip.current_version = version
    db.commit()
    return {
        "clip_id": clip.id,
        "version_id": version.id,
        "seed": best.seed,
        "score": round(best.score, 4),
        "candidates": [
            {"seed": c.seed, "score": round(c.score, 4), "rejected": c.rejected} for c in ranked
        ],
    }


@router.post("/generate", response_model=JobOut, status_code=202)
def generate(
    body: GenerateRequest,
    request: Request,
    db: DbSession,
    settings: SettingsDep,
    engine: EngineDep,
    jobs: JobsDep,
) -> JobOut:
    spec, section, track = build_spec(db, body, settings)
    section_id, track_id = section.id, track.id
    session_factory: sessionmaker[Session] = request.app.state.session_factory
    candidate_store: dict[tuple[int, int], list[ScoredCandidate]] = request.app.state.candidates
    params = {"controls": body.controls.model_dump()}

    def run(job: Job) -> dict[str, Any]:
        ranked = generate_candidates(engine, spec, job.cancel_event, job.emit)
        with session_factory() as worker_db:
            result = save_best(worker_db, section_id, track_id, spec, ranked, params)
        # Remaining valid candidates stay in memory for "Vary" during the session.
        candidate_store[(section_id, track_id)] = [c for c in ranked if c.rejected is None][1:]
        return result

    job = jobs.submit(run)
    return JobOut(**job.summary())


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str, jobs: JobsDep) -> JobOut:
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(404, f"job {job_id} not found")
    return JobOut(**job.summary())


@router.post("/jobs/{job_id}/cancel", response_model=JobOut)
def cancel_job(job_id: str, jobs: JobsDep) -> JobOut:
    job = jobs.cancel(job_id)
    if job is None:
        raise HTTPException(404, f"job {job_id} not found")
    return JobOut(**job.summary())


@router.get("/jobs/{job_id}/events")
async def job_events(job_id: str, jobs: JobsDep, request: Request) -> StreamingResponse:
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(404, f"job {job_id} not found")

    async def stream() -> AsyncIterator[str]:
        index = 0
        while True:
            events = job.events_since(index)
            index += len(events)
            for e in events:
                yield f"event: {e['event']}\ndata: {json.dumps(e['data'])}\n\n"
                if e["event"] in TERMINAL:
                    return
            if await request.is_disconnected():
                return
            await asyncio.sleep(0.05)

    return StreamingResponse(stream(), media_type="text/event-stream")
