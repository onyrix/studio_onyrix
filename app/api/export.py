"""MIDI export over the arrangement (sections in order, repeated instances included)."""

from __future__ import annotations

import re

from fastapi import APIRouter, Response

from app.api.deps import DbSession, get_or_404
from app.core.model import Note, Role
from app.core.timebase import TimeSignature, bars_to_ticks
from app.db.models import Project, Track
from app.midi_io import ExportTrack, build_midi, to_bytes

router = APIRouter(tags=["export"])


def _filename(name: str) -> str:
    return (re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "onyrix") + ".mid"


def arrangement_notes(project: Project, track: Track) -> tuple[Note, ...]:
    """Notes of one track over the whole arrangement, in absolute ticks."""
    ts = TimeSignature(project.ts_numerator, project.ts_denominator)
    sections = {s.id: s for s in project.sections}
    out: list[Note] = []
    offset = 0
    for item in project.arrangement:
        section = sections[item.section_id]
        slot = next((s for s in section.slots if s.track_id == track.id), None)
        version = slot.clip.current_version if slot is not None else None
        if version is not None:
            length = bars_to_ticks(section.bars, ts)
            for raw in version.notes:
                n = Note.from_dict(raw)
                if n.t < length:
                    out.append(Note(n.t + offset, n.p, min(n.d, length - n.t), n.v))
        offset += bars_to_ticks(section.bars, ts)
    return tuple(out)


def _export(project: Project, tracks: list[Track], filename: str) -> Response:
    export_tracks = [
        ExportTrack(
            name=t.name,
            program=t.program,
            is_drum=t.role == Role.DRUMS.value,
            notes=arrangement_notes(project, t),
        )
        for t in tracks
    ]
    mid = build_midi(
        project.name,
        project.bpm,
        TimeSignature(project.ts_numerator, project.ts_denominator),
        export_tracks,
    )
    return Response(
        content=to_bytes(mid),
        media_type="audio/midi",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/project/{project_id}.mid")
def export_project(project_id: int, db: DbSession) -> Response:
    project = get_or_404(db, Project, project_id)
    return _export(project, list(project.tracks), _filename(project.name))


@router.get("/export/track/{track_id}.mid")
def export_track(track_id: int, db: DbSession) -> Response:
    track = get_or_404(db, Track, track_id)
    project = track.project
    return _export(project, [track], _filename(f"{project.name}_{track.name}"))
