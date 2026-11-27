from fastapi.testclient import TestClient


def _project(client: TestClient, **fields: object) -> int:
    body = {"name": "Song", "key_tonic": 0, "key_mode": "major", "genre": "pop", **fields}
    project_id: int = client.post("/api/projects", json=body).json()["id"]
    return project_id


def test_diatonic(client: TestClient) -> None:
    out = client.get("/api/harmony/diatonic", params={"tonic": 9, "mode": "minor"}).json()
    assert [c["symbol"] for c in out] == ["Am", "Bdim", "C", "Dm", "Em", "F", "G"]
    assert [c["numeral"] for c in out] == ["i", "ii°", "III", "iv", "v", "VI", "VII"]
    assert client.get("/api/harmony/diatonic", params={"tonic": 12}).status_code == 422


def test_suggest_uses_the_section_name_and_length(client: TestClient) -> None:
    pid = _project(client)
    section = client.post(f"/api/projects/{pid}/sections", json={"name": "Chorus 2", "bars": 8})
    out = client.post(
        "/api/harmony/suggest", json={"project_id": pid, "section_id": section.json()["id"]}
    ).json()
    assert out["section_kind"] == "chorus"
    assert len(out["progressions"]) == 5
    first = out["progressions"][0]
    assert len(first["chords"]) == 8
    assert first["numerals"].startswith("I V vi IV")
    # Accepting a suggestion = PATCH the section grid with its symbols.
    symbols = [c["symbol"] for c in first["chords"]]
    patched = client.patch(f"/api/sections/{section.json()['id']}", json={"chord_grid": symbols})
    assert patched.status_code == 200


def test_suggest_explicit_kind_and_errors(client: TestClient) -> None:
    pid = _project(client, key_tonic=5)
    out = client.post(
        "/api/harmony/suggest",
        json={"project_id": pid, "section_kind": "outro", "bars": 4, "n": 2},
    ).json()
    assert out["section_kind"] == "outro"
    assert all(p["chords"][-1]["symbol"] == "F" for p in out["progressions"])
    # Spelled with flats in F major.
    assert "Bb" in {c["symbol"] for p in out["progressions"] for c in p["chords"]}
    bad = {"project_id": pid, "section_kind": "solo-guitar"}
    assert client.post("/api/harmony/suggest", json=bad).status_code == 422
    assert client.post("/api/harmony/suggest", json={"project_id": 999}).status_code == 404


def test_suggest_rejects_a_section_from_another_project(client: TestClient) -> None:
    pid = _project(client)
    other = _project(client)
    section = client.post(f"/api/projects/{other}/sections", json={"name": "Verse", "bars": 4})
    body = {"project_id": pid, "section_id": section.json()["id"]}
    assert client.post("/api/harmony/suggest", json=body).status_code == 422


def test_next(client: TestClient) -> None:
    pid = _project(client)
    out = client.post("/api/harmony/next", json={"project_id": pid, "chord": "C"}).json()
    assert out[0] == {
        "symbol": "F",
        "numeral": "IV",
        "root": 5,
        "quality": "",
        "pitch_class_set": [0, 5, 9],
        "kind": "functional",
    }
    assert {"functional", "borrowed"} <= {s["kind"] for s in out}
    bad = client.post("/api/harmony/next", json={"project_id": pid, "chord": "H7"})
    assert bad.status_code == 422


def test_parse(client: TestClient) -> None:
    pid = _project(client, key_tonic=5)
    out = client.post("/api/harmony/parse", json={"project_id": pid, "text": "F:2 Bb:2 C*2"})
    assert out.status_code == 200
    body = out.json()
    assert body["chord_text"] == "(F Bb) C*2"
    assert [(e["symbol"], e["numeral"], e["beats"]) for e in body["events"]] == [
        ("F", "I", 2),
        ("Bb", "IV", 2),
        ("C", "V", 8),
    ]
    bad = client.post("/api/harmony/parse", json={"project_id": pid, "text": "(F"})
    assert bad.status_code == 422
