"""SQLAlchemy ORM schema (CLAUDE.md section 5.2).

Notes are stored per ClipVersion as JSON `[{t, p, d, v}]`, ticks relative to the clip start.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    bpm: Mapped[float] = mapped_column(Float, default=120.0)
    ts_numerator: Mapped[int] = mapped_column(Integer, default=4)
    ts_denominator: Mapped[int] = mapped_column(Integer, default=4)
    key_tonic: Mapped[int] = mapped_column(Integer, default=0)
    key_mode: Mapped[str] = mapped_column(String(16), default="major")
    genre: Mapped[str] = mapped_column(String(64), default="")
    chord_grid: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    tracks: Mapped[list[Track]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Track.position"
    )
    sections: Mapped[list[Section]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    arrangement: Mapped[list[ArrangementItem]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="ArrangementItem.position"
    )


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(16))
    program: Mapped[int] = mapped_column(Integer, default=0)
    name: Mapped[str] = mapped_column(String(200))
    mute: Mapped[bool] = mapped_column(default=False)
    solo: Mapped[bool] = mapped_column(default=False)
    position: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped[Project] = relationship(back_populates="tracks")
    clips: Mapped[list[Clip]] = relationship(back_populates="track", cascade="all, delete-orphan")


class Clip(Base):
    __tablename__ = "clips"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id", ondelete="CASCADE"))
    bars: Mapped[int] = mapped_column(Integer)
    locked: Mapped[bool] = mapped_column(default=False)
    current_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("clip_versions.id", ondelete="SET NULL", use_alter=True), nullable=True
    )

    track: Mapped[Track] = relationship(back_populates="clips")
    versions: Mapped[list[ClipVersion]] = relationship(
        back_populates="clip",
        cascade="all, delete-orphan",
        foreign_keys="ClipVersion.clip_id",
        order_by="ClipVersion.id",
    )
    current_version: Mapped[ClipVersion | None] = relationship(
        foreign_keys=[current_version_id], post_update=True
    )


class ClipVersion(Base):
    __tablename__ = "clip_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    clip_id: Mapped[int] = mapped_column(ForeignKey("clips.id", ondelete="CASCADE"))
    notes: Mapped[list[dict[str, int]]] = mapped_column(JSON, default=list)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(16))  # model | manual | import
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    params: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    clip: Mapped[Clip] = relationship(back_populates="versions", foreign_keys=[clip_id])


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    bars: Mapped[int] = mapped_column(Integer)
    # One {root, quality, pitch_class_set} per bar; empty = cycle the project's chord_grid.
    chord_grid: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)

    project: Mapped[Project] = relationship(back_populates="sections")
    slots: Mapped[list[SectionSlot]] = relationship(
        back_populates="section", cascade="all, delete-orphan"
    )


class SectionSlot(Base):
    """Which clip plays on a given track inside a section."""

    __tablename__ = "section_slots"

    section_id: Mapped[int] = mapped_column(
        ForeignKey("sections.id", ondelete="CASCADE"), primary_key=True
    )
    track_id: Mapped[int] = mapped_column(
        ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True
    )
    clip_id: Mapped[int] = mapped_column(ForeignKey("clips.id", ondelete="CASCADE"))

    section: Mapped[Section] = relationship(back_populates="slots")


class ArrangementItem(Base):
    """One section instance in the arrangement; the same section may appear several times."""

    __tablename__ = "arrangement_items"
    __table_args__ = (UniqueConstraint("project_id", "position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"))

    project: Mapped[Project] = relationship(back_populates="arrangement")
