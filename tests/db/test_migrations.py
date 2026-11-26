from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Engine, inspect, select
from sqlalchemy.orm import Session

from app.db import models
from app.db.base import Base
from app.db.migrate import upgrade_to_head
from app.db.session import make_engine

EXPECTED_TABLES = {
    "projects",
    "tracks",
    "clips",
    "clip_versions",
    "sections",
    "section_slots",
    "arrangement_items",
}


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    upgrade_to_head(url)
    eng = make_engine(url)
    yield eng
    eng.dispose()


def test_migrates_from_empty(engine: Engine) -> None:
    tables = set(inspect(engine).get_table_names())
    assert tables >= EXPECTED_TABLES
    assert "alembic_version" in tables


def test_0002_upgrades_existing_sections(tmp_path: Path) -> None:
    from alembic import command
    from sqlalchemy import text

    from app.db.migrate import alembic_config

    url = f"sqlite:///{(tmp_path / 'old.db').as_posix()}"
    cfg = alembic_config(url)
    command.upgrade(cfg, "0001")
    eng = make_engine(url)
    with eng.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO projects (id, name, bpm, ts_numerator, ts_denominator, key_tonic, "
                "key_mode, genre, chord_grid, created_at, updated_at) VALUES "
                "(1, 'p', 120, 4, 4, 0, 'major', '', '[]', '2026-01-01', '2026-01-01')"
            )
        )
        conn.execute(
            text("INSERT INTO sections (id, project_id, name, bars) VALUES (1, 1, 'A', 4)")
        )
    command.upgrade(cfg, "head")
    with eng.connect() as conn:
        assert conn.execute(text("SELECT chord_grid FROM sections")).scalar_one() == "[]"
    eng.dispose()


def test_migration_matches_models(engine: Engine) -> None:
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == []


def test_clip_fk_to_current_version_exists(engine: Engine) -> None:
    fks = inspect(engine).get_foreign_keys("clips")
    assert any(fk["referred_table"] == "clip_versions" for fk in fks)


def test_orm_round_trip_and_cascade(engine: Engine) -> None:
    with Session(engine) as session:
        project = models.Project(name="Demo", bpm=96.0, chord_grid=[])
        track = models.Track(project=project, role="bass", program=33, name="Bass")
        clip = models.Clip(track=track, bars=4)
        version = models.ClipVersion(
            clip=clip, notes=[{"t": 0, "p": 40, "d": 240, "v": 100}], seed=7, source="model"
        )
        session.add_all([project, version])
        session.flush()
        clip.current_version = version
        section = models.Section(project=project, name="Verse", bars=4)
        session.add(section)
        session.flush()
        section.slots.append(models.SectionSlot(track_id=track.id, clip_id=clip.id))
        project.arrangement.extend(
            [
                models.ArrangementItem(position=0, section_id=section.id),
                models.ArrangementItem(position=1, section_id=section.id),
            ]
        )
        session.commit()

        stored = session.scalars(select(models.Clip)).one()
        assert stored.current_version is not None
        assert stored.current_version.seed == 7
        assert stored.current_version.notes[0]["p"] == 40
        assert [item.section_id for item in project.arrangement] == [section.id, section.id]

        session.delete(project)
        session.commit()
        for table in (models.Clip, models.ClipVersion, models.SectionSlot, models.ArrangementItem):
            assert session.scalars(select(table)).all() == []
