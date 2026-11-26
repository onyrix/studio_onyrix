import threading
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.harmony import parse_chord
from app.core.model import Role
from tests.api.conftest import make_app, read_events
from tests.fakes import FakeEngine


def generate(client: TestClient, project: dict[str, Any], role: str, **extra: Any) -> str:
    body = {
        "section_id": project["section"]["id"],
        "track_id": project["tracks"][role]["id"],
        **extra,
    }
    response = client.post("/api/generate", json=body)
    assert response.status_code == 202, response.text
    job_id: str = response.json()["id"]
    return job_id


def run_to_end(client: TestClient, project: dict[str, Any], role: str, **extra: Any) -> Any:
    job_id = generate(client, project, role, **extra)
    events = read_events(client, job_id)
    assert events[-1][0] == "done", events
    return events


def test_generate_streams_progress_and_saves_best(
    client: TestClient, project: dict[str, Any]
) -> None:
    events = run_to_end(client, project, "bass", seed=1000, n_candidates=4)
    names = [e for e, _ in events]
    assert names[:3] == ["queued", "started", "sampling"]
    assert names.count("candidate") == 4

    result = events[-1][1]
    assert len(result["candidates"]) == 4
    scores = [c["score"] for c in result["candidates"] if c["rejected"] is None]
    assert result["score"] == max(scores)

    clip = client.get(f"/api/clips/{result['clip_id']}").json()
    version = clip["current_version"]
    assert (version["source"], version["seed"]) == ("model", result["seed"])
    assert version["score"] == pytest.approx(result["score"], abs=1e-4)  # result is rounded
    assert version["params"]["controls"]["harmony"] == "normal"
    assert version["params"]["request_seed"] == 1000
    assert all(28 <= n["p"] <= 55 and n["t"] % 120 == 0 for n in version["notes"])

    section = client.get(f"/api/projects/{project['id']}").json()["sections"][0]
    assert section["slots"] == {str(project["tracks"]["bass"]["id"]): clip["id"]}


def test_same_seed_is_reproducible_and_versions_are_kept(
    client: TestClient, project: dict[str, Any]
) -> None:
    first = run_to_end(client, project, "bass", seed=7)[-1][1]
    second = run_to_end(client, project, "bass", seed=7)[-1][1]
    assert first["clip_id"] == second["clip_id"]
    assert first["seed"] == second["seed"]
    versions = client.get(f"/api/clips/{first['clip_id']}/versions").json()
    assert len(versions) == 2
    assert versions[0]["notes"] == versions[1]["notes"]


def test_context_chords_and_key_reach_the_engine(
    client: TestClient, project: dict[str, Any], engine: FakeEngine
) -> None:
    run_to_end(client, project, "drums", seed=1)
    run_to_end(client, project, "bass", seed=2)
    spec = engine.calls[-1]
    assert spec.target_role is Role.BASS
    assert [c.role for c in spec.context] == [Role.DRUMS]
    assert spec.context[0].notes
    assert spec.chords == tuple(parse_chord(c) for c in ("Am", "F", "C", "G"))
    assert (spec.key.tonic, spec.key.mode.value) == (9, "minor")  # type: ignore[union-attr]
    assert (spec.bpm, spec.bars, spec.genre) == (100, 4, "pop")


def test_section_chord_grid_overrides_project(
    client: TestClient, project: dict[str, Any], engine: FakeEngine
) -> None:
    client.patch(f"/api/sections/{project['section']['id']}", json={"chord_grid": ["Dm", "E7"]})
    run_to_end(client, project, "lead", seed=3)
    assert [c.root for c in engine.calls[-1].chords] == [2, 4, 2, 4]  # type: ignore[union-attr]


def test_locked_clip_cannot_be_regenerated(client: TestClient, project: dict[str, Any]) -> None:
    clip_id = run_to_end(client, project, "bass", seed=1)[-1][1]["clip_id"]
    client.patch(f"/api/clips/{clip_id}", json={"locked": True})
    body = {"section_id": project["section"]["id"], "track_id": project["tracks"]["bass"]["id"]}
    assert client.post("/api/generate", json=body).status_code == 409


def test_manual_edit_creates_version(client: TestClient, project: dict[str, Any]) -> None:
    clip_id = run_to_end(client, project, "bass", seed=1)[-1][1]["clip_id"]
    edited = client.patch(
        f"/api/clips/{clip_id}", json={"notes": [{"t": 0, "p": 33, "d": 480, "v": 100}]}
    ).json()
    assert edited["current_version"]["source"] == "manual"
    assert len(client.get(f"/api/clips/{clip_id}/versions").json()) == 2
    too_long = client.patch(
        f"/api/clips/{clip_id}", json={"notes": [{"t": 7680, "p": 33, "d": 480, "v": 100}]}
    )
    assert too_long.status_code == 422


def test_validation_errors(client: TestClient, project: dict[str, Any]) -> None:
    track = project["tracks"]["bass"]["id"]
    section = project["section"]["id"]
    assert (
        client.post("/api/generate", json={"section_id": 999, "track_id": track}).status_code == 404
    )
    wrong_bars = {"section_id": section, "track_id": track, "bars": 8}
    assert client.post("/api/generate", json=wrong_bars).status_code == 422
    too_many = {"section_id": section, "track_id": track, "n_candidates": 9}
    assert client.post("/api/generate", json=too_many).status_code == 422


def test_cancel_running_job(tmp_path: Path) -> None:

    gate = threading.Event()
    app = make_app(tmp_path, FakeEngine(block=gate))
    with TestClient(app) as client:
        pid = client.post("/api/projects", json={"name": "c"}).json()["id"]
        track = client.post(f"/api/projects/{pid}/tracks", json={"role": "lead"}).json()["id"]
        sec = client.post(f"/api/projects/{pid}/sections", json={"name": "A", "bars": 4}).json()
        body = {"section_id": sec["id"], "track_id": track}
        first = client.post("/api/generate", json=body).json()["id"]
        second = client.post("/api/generate", json=body).json()["id"]
        assert client.get(f"/api/jobs/{second}").json()["status"] == "queued"  # serialized

        client.post(f"/api/jobs/{first}/cancel")
        client.post(f"/api/jobs/{second}/cancel")
        assert read_events(client, first)[-1][0] == "cancelled"
        assert read_events(client, second)[-1][0] == "cancelled"
        section = client.get(f"/api/projects/{pid}").json()["sections"][0]
        assert section["slots"] == {}


def test_no_valid_candidate_is_an_error(tmp_path: Path) -> None:
    from app.gen.engine import RawCandidate

    class EmptyEngine(FakeEngine):
        def sample(self, spec: Any, cancel: Any = None, progress: Any = None) -> Any:
            return [RawCandidate(seed=spec.seed, notes=())]

    app = make_app(tmp_path, EmptyEngine())
    with TestClient(app) as client:
        pid = client.post("/api/projects", json={"name": "e"}).json()["id"]
        track = client.post(f"/api/projects/{pid}/tracks", json={"role": "lead"}).json()["id"]
        sec = client.post(f"/api/projects/{pid}/sections", json={"name": "A", "bars": 4}).json()
        job = client.post("/api/generate", json={"section_id": sec["id"], "track_id": track})
        name, data = read_events(client, job.json()["id"])[-1]
        assert name == "error" and "no valid candidate (empty)" in data["message"]


def test_models_info(client: TestClient) -> None:
    assert client.get("/api/models/info").json()["model"] == "fake"
