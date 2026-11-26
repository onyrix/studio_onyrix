from typing import Any

from fastapi.testclient import TestClient


def test_project_crud_and_chord_grid(client: TestClient) -> None:
    created = client.post("/api/projects", json={"name": "Song", "chord_grid": ["Am7", "D"]})
    assert created.status_code == 201
    body = created.json()
    assert body["chord_grid"][0] == {
        "root": 9,
        "quality": "m7",
        "pitch_class_set": [0, 4, 7, 9],
        "symbol": "Am7",
    }
    pid = body["id"]

    patched = client.patch(f"/api/projects/{pid}", json={"bpm": 90, "genre": "jazz"}).json()
    assert (patched["bpm"], patched["genre"], patched["name"]) == (90, "jazz", "Song")
    assert [p["id"] for p in client.get("/api/projects").json()] == [pid]

    assert client.delete(f"/api/projects/{pid}").status_code == 204
    assert client.get(f"/api/projects/{pid}").status_code == 404


def test_invalid_input_is_rejected(client: TestClient) -> None:
    assert client.post("/api/projects", json={"name": "x", "chord_grid": ["H7"]}).status_code == 422
    assert client.post("/api/projects", json={"name": "x", "ts_denominator": 3}).status_code == 422
    pid = client.post("/api/projects", json={"name": "x"}).json()["id"]
    bad_role = client.post(f"/api/projects/{pid}/tracks", json={"role": "kazoo"})
    assert bad_role.status_code == 422


def test_tracks_get_role_defaults(client: TestClient, project: dict[str, Any]) -> None:
    bass = project["tracks"]["bass"]
    assert (bass["program"], bass["name"], bass["position"]) == (33, "Bass", 1)
    patched = client.patch(f"/api/tracks/{bass['id']}", json={"mute": True, "program": 38})
    assert (patched.json()["mute"], patched.json()["program"]) == (True, 38)


def test_arrangement_reorder_duplicate_and_delete(
    client: TestClient, project: dict[str, Any]
) -> None:
    pid = project["id"]
    verse = project["section"]["id"]
    chorus = client.post(f"/api/projects/{pid}/sections", json={"name": "Chorus", "bars": 8})
    chorus_id = chorus.json()["id"]
    assert client.get(f"/api/projects/{pid}").json()["arrangement"] == [verse, chorus_id]

    order = [chorus_id, verse, chorus_id]  # reorder + duplicate instance
    put = client.put(f"/api/projects/{pid}/arrangement", json={"section_ids": order})
    assert put.status_code == 200 and put.json()["arrangement"] == order

    assert client.delete(f"/api/sections/{verse}").status_code == 204
    assert client.get(f"/api/projects/{pid}").json()["arrangement"] == [chorus_id, chorus_id]

    other = client.post("/api/projects", json={"name": "other"}).json()["id"]
    foreign = client.post(f"/api/projects/{other}/sections", json={"name": "X", "bars": 4})
    bad = client.put(
        f"/api/projects/{pid}/arrangement", json={"section_ids": [foreign.json()["id"]]}
    )
    assert bad.status_code == 422
