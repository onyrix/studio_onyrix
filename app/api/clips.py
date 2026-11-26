"""Clips and their version history."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.deps import DbSession, get_or_404
from app.api.schemas import ClipOut, ClipPatch, ClipVersionOut
from app.core.model import ClipSource
from app.core.timebase import TimeSignature, bars_to_ticks
from app.db.models import Clip, ClipVersion, Project

router = APIRouter(tags=["clips"])


def clip_out(clip: Clip) -> ClipOut:
    version = clip.current_version
    return ClipOut(
        id=clip.id,
        track_id=clip.track_id,
        bars=clip.bars,
        locked=clip.locked,
        current_version=ClipVersionOut.model_validate(version) if version else None,
    )


@router.get("/projects/{project_id}/clips", response_model=list[ClipOut])
def list_project_clips(project_id: int, db: DbSession) -> list[ClipOut]:
    """Every clip of the project with its current notes, so the UI loads them in one call."""
    project = get_or_404(db, Project, project_id)
    return [clip_out(clip) for track in project.tracks for clip in track.clips]


@router.get("/clips/{clip_id}", response_model=ClipOut)
def get_clip(clip_id: int, db: DbSession) -> ClipOut:
    return clip_out(get_or_404(db, Clip, clip_id))


@router.patch("/clips/{clip_id}", response_model=ClipOut)
def patch_clip(clip_id: int, body: ClipPatch, db: DbSession) -> ClipOut:
    clip = get_or_404(db, Clip, clip_id)
    if body.notes is not None:
        if clip.locked and body.locked is not False:
            raise HTTPException(409, "clip is locked")
        project = clip.track.project
        length = bars_to_ticks(
            clip.bars, TimeSignature(project.ts_numerator, project.ts_denominator)
        )
        if any(n.t + n.d > length for n in body.notes):
            raise HTTPException(422, "notes must end within the clip")
        version = ClipVersion(
            clip=clip,
            notes=[n.model_dump() for n in sorted(body.notes, key=lambda n: (n.t, n.p))],
            seed=None,
            source=ClipSource.MANUAL.value,
            params={},
        )
        db.add(version)
        db.flush()
        clip.current_version = version
    if body.locked is not None:
        clip.locked = body.locked
    db.commit()
    return clip_out(clip)


@router.get("/clips/{clip_id}/versions", response_model=list[ClipVersionOut])
def list_versions(clip_id: int, db: DbSession) -> list[ClipVersion]:
    return list(get_or_404(db, Clip, clip_id).versions)
