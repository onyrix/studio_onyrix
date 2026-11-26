"""M2 acceptance with the real model through the API: 4 candidates, best by S, same seed."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.gen.engine import MidiGptEngine
from tests.api.conftest import make_app, read_events

pytestmark = pytest.mark.inference
pytest.importorskip("midigpt.inference")


def test_generate_via_api_is_reproducible(tmp_path: Path) -> None:
    app = make_app(tmp_path, MidiGptEngine("prism_medium", "yellow_medium", device="cpu"))
    with TestClient(app) as client:
        pid = client.post(
            "/api/projects",
            json={
                "name": "M2",
                "bpm": 100,
                "key_tonic": 9,
                "key_mode": "minor",
                "genre": "pop",
                "chord_grid": ["Am", "F", "C", "G"],
            },
        ).json()["id"]
        bass = client.post(f"/api/projects/{pid}/tracks", json={"role": "bass"}).json()["id"]
        sec = client.post(f"/api/projects/{pid}/sections", json={"name": "A", "bars": 4}).json()
        body = {"section_id": sec["id"], "track_id": bass, "seed": 2024, "n_candidates": 4}

        results = []
        for _ in range(2):
            job = client.post("/api/generate", json=body).json()["id"]
            name, result = read_events(client, job)[-1]
            assert name == "done", result
            results.append(result)

        first, second = results
        assert len(first["candidates"]) == 4
        valid = [c["score"] for c in first["candidates"] if c["rejected"] is None]
        assert first["score"] == max(valid)
        assert (first["seed"], first["score"]) == (second["seed"], second["score"])
        versions = client.get(f"/api/clips/{first['clip_id']}/versions").json()
        assert versions[0]["notes"] == versions[1]["notes"]
        assert all(28 <= n["p"] <= 55 for n in versions[0]["notes"])
