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
    assert (first["id"], first["numerals"], first["chord_text"]) == (
        "axis",
        "I V vi IV",
        "C G Am F",
    )
    assert [c["beats"] for c in first["chords"]] == [4, 4, 4, 4]
    assert "bright" in first["moods"]
    # Accepting a suggestion = PATCH the section grid with its text.
    sid = section.json()["id"]
    patched = client.patch(f"/api/sections/{sid}", json={"chord_grid": first["chord_text"]})
    assert patched.status_code == 200


def test_suggest_keeps_harmonic_rhythm_and_filters_moods(client: TestClient) -> None:
    pid = _project(client, genre="jazz")
    out = client.post(
        "/api/harmony/suggest",
        json={"project_id": pid, "section_kind": "verse", "moods": ["calm"], "n": 3},
    ).json()
    assert all("calm" in p["moods"] for p in out["progressions"])
    first = out["progressions"][0]
    assert (first["chord_text"], first["numerals"]) == ("Dm7 G7 Cmaj7*2", "ii7 V7 Imaj7*2")
    assert [c["beats"] for c in first["chords"]] == [4, 4, 8]
    bad = {"project_id": pid, "moods": ["angry"]}
    assert client.post("/api/harmony/suggest", json=bad).status_code == 422


def test_suggest_explicit_kind_and_errors(client: TestClient) -> None:
    pid = _project(client, key_tonic=5)
    out = client.post(
        "/api/harmony/suggest",
        json={"project_id": pid, "section_kind": "outro", "bars": 4, "n": 2},
    ).json()
    assert out["section_kind"] == "outro"
    assert len(out["progressions"]) == 2
    # Spelled with flats in F major (borrowed bVI / bVII as Db / Eb, never C# / D#).
    symbols = {c["symbol"] for p in out["progressions"] for c in p["chords"]}
    assert not any("#" in s for s in symbols)
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
