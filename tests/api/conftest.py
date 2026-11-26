from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.base import Base
from app.db.session import make_engine
from app.main import create_app
from tests.fakes import FakeEngine


@pytest.fixture
def engine() -> FakeEngine:
    return FakeEngine()


def make_app(tmp_path: Path, engine: Any) -> FastAPI:
    """App on a temporary SQLite file: the generation worker writes from its own thread, which
    an in-memory database (one shared connection and transaction) cannot isolate."""
    url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    Base.metadata.create_all(make_engine(url))
    settings = Settings(database_url=url, soundfont_dir=str(tmp_path / "soundfonts"))
    return create_app(settings, engine=engine)


@pytest.fixture
def client(engine: FakeEngine, tmp_path: Path) -> Iterator[TestClient]:
    with TestClient(make_app(tmp_path, engine)) as c:
        yield c


def read_events(client: TestClient, job_id: str) -> list[tuple[str, dict[str, Any]]]:
    import json

    events = []
    with client.stream("GET", f"/api/jobs/{job_id}/events") as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        name = None
        for line in response.iter_lines():
            if line.startswith("event: "):
                name = line.removeprefix("event: ")
            elif line.startswith("data: ") and name is not None:
                events.append((name, json.loads(line.removeprefix("data: "))))
    return events


@pytest.fixture
def project(client: TestClient) -> dict[str, Any]:
    """Project in A minor with drums, bass and lead tracks and one 4-bar section."""
    p = client.post(
        "/api/projects",
        json={
            "name": "Demo",
            "bpm": 100,
            "key_tonic": 9,
            "key_mode": "minor",
            "genre": "pop",
            "chord_grid": ["Am", "F", "C", "G"],
        },
    ).json()
    tracks = {
        role: client.post(f"/api/projects/{p['id']}/tracks", json={"role": role}).json()
        for role in ("drums", "bass", "lead")
    }
    section = client.post(
        f"/api/projects/{p['id']}/sections", json={"name": "Verse", "bars": 4}
    ).json()
    return {"id": p["id"], "tracks": tracks, "section": section}
