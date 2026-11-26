"""Projects, tracks, sections and arrangement."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import DbSession, get_or_404
from app.api.schemas import (
    ArrangementIn,
    ProjectCreate,
    ProjectOut,
    ProjectPatch,
    ProjectSummary,
    SectionCreate,
    SectionOut,
    SectionPatch,
    TrackCreate,
    TrackOut,
    TrackPatch,
)
from app.core.roles import role_spec
from app.db.models import ArrangementItem, Project, Section, Track

router = APIRouter(tags=["projects"])


def section_out(section: Section) -> SectionOut:
    return SectionOut(
        id=section.id,
        name=section.name,
        bars=section.bars,
        chord_grid=section.chord_grid,
        slots={slot.track_id: slot.clip_id for slot in section.slots},
    )


def project_out(project: Project) -> ProjectOut:
    return ProjectOut(
        id=project.id,
        name=project.name,
        bpm=project.bpm,
        ts_numerator=project.ts_numerator,
        ts_denominator=project.ts_denominator,
        key_tonic=project.key_tonic,
        key_mode=project.key_mode,  # type: ignore[arg-type]
        genre=project.genre,
        chord_grid=project.chord_grid,
        tracks=[TrackOut.model_validate(t) for t in project.tracks],
        sections=[section_out(s) for s in project.sections],
        arrangement=[item.section_id for item in project.arrangement],
    )


@router.get("/projects", response_model=list[ProjectSummary])
def list_projects(db: DbSession) -> list[Project]:
    return list(db.scalars(select(Project).order_by(Project.id)))


@router.post("/projects", response_model=ProjectOut, status_code=201)
def create_project(body: ProjectCreate, db: DbSession) -> ProjectOut:
    project = Project(**body.model_dump(mode="json"))
    db.add(project)
    db.commit()
    return project_out(project)


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: DbSession) -> ProjectOut:
    return project_out(get_or_404(db, Project, project_id))


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def patch_project(project_id: int, body: ProjectPatch, db: DbSession) -> ProjectOut:
    project = get_or_404(db, Project, project_id)
    for key, value in body.model_dump(mode="json", exclude_unset=True).items():
        if value is not None:
            setattr(project, key, value)
    db.commit()
    return project_out(project)


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, db: DbSession) -> Response:
    db.delete(get_or_404(db, Project, project_id))
    db.commit()
    return Response(status_code=204)


@router.post("/projects/{project_id}/tracks", response_model=TrackOut, status_code=201)
def create_track(project_id: int, body: TrackCreate, db: DbSession) -> Track:
    project = get_or_404(db, Project, project_id)
    spec = role_spec(body.role)
    track = Track(
        role=body.role.value,
        name=body.name or body.role.value.capitalize(),
        program=body.program if body.program is not None else spec.program,
        position=len(project.tracks),
    )
    project.tracks.append(track)
    db.commit()
    return track


@router.patch("/tracks/{track_id}", response_model=TrackOut)
def patch_track(track_id: int, body: TrackPatch, db: DbSession) -> Track:
    track = get_or_404(db, Track, track_id)
    for key, value in body.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(track, key, value)
    db.commit()
    return track


@router.delete("/tracks/{track_id}", status_code=204)
def delete_track(track_id: int, db: DbSession) -> Response:
    db.delete(get_or_404(db, Track, track_id))
    db.commit()
    return Response(status_code=204)


@router.post("/projects/{project_id}/sections", response_model=SectionOut, status_code=201)
def create_section(project_id: int, body: SectionCreate, db: DbSession) -> SectionOut:
    """Create a section and append one instance of it to the arrangement."""
    project = get_or_404(db, Project, project_id)
    section = Section(name=body.name, bars=body.bars, chord_grid=body.chord_grid)
    project.sections.append(section)
    db.flush()
    project.arrangement.append(
        ArrangementItem(position=len(project.arrangement), section_id=section.id)
    )
    db.commit()
    return section_out(section)


@router.patch("/sections/{section_id}", response_model=SectionOut)
def patch_section(section_id: int, body: SectionPatch, db: DbSession) -> SectionOut:
    section = get_or_404(db, Section, section_id)
    for key, value in body.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(section, key, value)
    db.commit()
    return section_out(section)


@router.delete("/sections/{section_id}", status_code=204)
def delete_section(section_id: int, db: DbSession) -> Response:
    section = get_or_404(db, Section, section_id)
    project = section.project
    db.delete(section)
    db.flush()
    db.expire(project, ["arrangement", "sections"])  # DB cascade removed its instances
    _renumber(db, project)
    db.commit()
    return Response(status_code=204)


@router.put("/projects/{project_id}/arrangement", response_model=ProjectOut)
def put_arrangement(project_id: int, body: ArrangementIn, db: DbSession) -> ProjectOut:
    project = get_or_404(db, Project, project_id)
    own = {s.id for s in project.sections}
    unknown = [sid for sid in body.section_ids if sid not in own]
    if unknown:
        raise HTTPException(422, f"sections not in project: {unknown}")
    project.arrangement.clear()
    db.flush()  # delete old rows before reusing positions (unique constraint)
    for position, section_id in enumerate(body.section_ids):
        project.arrangement.append(ArrangementItem(position=position, section_id=section_id))
    db.commit()
    db.refresh(project)
    return project_out(project)


def _renumber(db: Session, project: Project) -> None:
    items = list(project.arrangement)
    project.arrangement.clear()
    db.flush()  # delete old rows before reusing positions (unique constraint)
    for position, item in enumerate(items):
        project.arrangement.append(ArrangementItem(position=position, section_id=item.section_id))
