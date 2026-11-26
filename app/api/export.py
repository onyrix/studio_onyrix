"""MIDI export over the arrangement (sections in order, repeated instances included).

`start` / `end` select a range of section instances (end exclusive), e.g. one section for
playback. `loop=true` adds loop markers spanning the range (playback files only).
"""

from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException, Query, Response

from app.api.deps import DbSession, get_or_404
from app.core.model import Note, Role
from app.core.timebase import TimeSignature, bars_to_ticks
from app.db.models import Project, Track
from app.midi_io import ExportTrack, build_midi, to_bytes

router = APIRouter(tags=["export"])


def _filename(name: str) -> str:
    return (re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "onyrix") + ".mid"


def _range(project: Project, start: int, end: int | None) -> tuple[int, int]:
    count = len(project.arrangement)
    stop = count if end is None else end
    if not 0 <= start < stop <= count:
        raise HTTPException(422, f"invalid instance range [{start}, {stop}) for {count} instances")
    return start, stop


def arrangement_notes(project: Project, track: Track, start: int, end: int) -> tuple[Note, ...]:
    """Notes of one track over arrangement instances [start, end), in ticks from `start`."""
    ts = TimeSignature(project.ts_numerator, project.ts_denominator)
    sections = {s.id: s for s in project.sections}
    out: list[Note] = []
    offset = 0
    for item in project.arrangement[start:end]:
        section = sections[item.section_id]
        length = bars_to_ticks(section.bars, ts)
        slot = next((s for s in section.slots if s.track_id == track.id), None)
        version = slot.clip.current_version if slot is not None else None
        if version is not None:
            for raw in version.notes:
                n = Note.from_dict(raw)
                if n.t < length:
                    out.append(Note(n.t + offset, n.p, min(n.d, length - n.t), n.v))
        offset += length
    return tuple(out)


def range_ticks(project: Project, start: int, end: int) -> int:
    ts = TimeSignature(project.ts_numerator, project.ts_denominator)
    sections = {s.id: s for s in project.sections}
    return sum(
        bars_to_ticks(sections[i.section_id].bars, ts) for i in project.arrangement[start:end]
    )


def _export(
    project: Project,
    tracks: list[Track],
    filename: str,
    start: int,
    end: int | None,
    loop: bool,
) -> Response:
    first, stop = _range(project, start, end) if project.arrangement else (0, 0)
    export_tracks = [
        ExportTrack(
            name=t.name,
            program=t.program,
            is_drum=t.role == Role.DRUMS.value,
            notes=arrangement_notes(project, t, first, stop),
        )
        for t in tracks
    ]
    mid = build_midi(
        project.name,
        project.bpm,
        TimeSignature(project.ts_numerator, project.ts_denominator),
        export_tracks,
        loop_ticks=range_ticks(project, first, stop) if loop and stop > first else None,
    )
    return Response(
        content=to_bytes(mid),
        media_type="audio/midi",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/project/{project_id}.mid")
def export_project(
    project_id: int,
    db: DbSession,
    start: int = Query(default=0, ge=0),
    end: int | None = Query(default=None, ge=1),
    loop: bool = False,
) -> Response:
    project = get_or_404(db, Project, project_id)
    return _export(project, list(project.tracks), _filename(project.name), start, end, loop)


@router.get("/export/track/{track_id}.mid")
def export_track(track_id: int, db: DbSession) -> Response:
    track = get_or_404(db, Track, track_id)
    project = track.project
    return _export(project, [track], _filename(f"{project.name}_{track.name}"), 0, None, loop=False)
