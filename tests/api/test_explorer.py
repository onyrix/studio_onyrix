from fastapi.testclient import TestClient

from app.core.operators import OPERATORS


def _project(client: TestClient, **fields: object) -> int:
    body = {"name": "Song", "key_tonic": 0, "key_mode": "major", "genre": "pop", **fields}
    project_id: int = client.post("/api/projects", json=body).json()["id"]
    return project_id


def test_explore_is_reproducible_and_follows_audacity(client: TestClient) -> None:
    pid = _project(client)
    body = {"project_id": pid, "section_kind": "chorus", "length": 4, "seed": 3, "n": 4}
    calm = client.post("/api/harmony/explore", json={**body, "audacity": 0.0}).json()
    wild = client.post("/api/harmony/explore", json={**body, "audacity": 1.0}).json()
    assert calm["source"] == "library"  # no corpus imported in tests
    assert calm == client.post("/api/harmony/explore", json={**body, "audacity": 0.0}).json()
    first = calm["progressions"][0]
    assert len(first["chords"]) == 4
    assert first["chord_text"] and first["numerals"]
    assert calm["progressions"][0]["surprise"] <= wild["progressions"][0]["surprise"]
    assert 0 <= wild["progressions"][0]["surprise_level"] <= 1


def test_explore_minor_and_validation(client: TestClient) -> None:
    pid = _project(client, key_tonic=9, key_mode="minor")
    out = client.post("/api/harmony/explore", json={"project_id": pid, "audacity": 0.5}).json()
    assert out["progressions"]
    bad = client.post("/api/harmony/explore", json={"project_id": pid, "audacity": 2})
    assert bad.status_code == 422


def test_operators_list(client: TestClient) -> None:
    ops = client.get("/api/harmony/operators").json()
    assert {op["id"] for op in ops} == set(OPERATORS)
    assert {op["scope"] for op in ops} == {"chord", "progression"}


def test_transform(client: TestClient) -> None:
    pid = _project(client)
    body = {"project_id": pid, "text": "C G Am F", "operator": "borrow", "index": 3}
    out = client.post("/api/harmony/transform", json=body).json()
    assert (out["chord_text"], out["numerals"]) == ("C G Am Fm", "I V vi iv")
    assert out["surprise"] > 0
    not_applicable = {**body, "operator": "tritone_sub", "index": 2}
    response = client.post("/api/harmony/transform", json=not_applicable)
    assert response.status_code == 422
    unknown = client.post("/api/harmony/transform", json={**body, "operator": "nope"})
    assert unknown.status_code == 404


def test_surprise_in_parse_and_suggest(client: TestClient) -> None:
    pid = _project(client)
    common = client.post("/api/harmony/parse", json={"project_id": pid, "text": "C G Am F"})
    odd = client.post("/api/harmony/parse", json={"project_id": pid, "text": "C Gb A Eb"})
    assert common.json()["numerals"] == "I V vi IV"
    assert common.json()["surprise"] < odd.json()["surprise"]
    suggested = client.post("/api/harmony/suggest", json={"project_id": pid, "n": 3}).json()
    assert all("surprise_level" in p for p in suggested["progressions"])
