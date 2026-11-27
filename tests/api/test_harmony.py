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


def test_audition_returns_a_playable_midi(client: TestClient) -> None:
    import io

    import mido

    pid = _project(client)
    response = client.get(
        "/api/harmony/audition.mid", params={"project_id": pid, "text": "C (Am F) G*2"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/midi"
    mid = mido.MidiFile(file=io.BytesIO(response.content))
    chords, bass = mid.tracks[1], mid.tracks[2]
    starts = [m for m in chords if m.type == "note_on"]
    assert len([m for m in bass if m.type == "note_on"]) == 4  # one root per chord
    assert len(starts) == 12  # four triads
    bad = client.get("/api/harmony/audition.mid", params={"project_id": pid, "text": "(C"})
    assert bad.status_code == 422


def test_kits_are_in_the_project_mode_and_key(client: TestClient) -> None:
    pid = _project(client, key_tonic=9, key_mode="minor")
    kits = client.get("/api/harmony/kits", params={"project_id": pid}).json()
    assert kits and all(k["id"] for k in kits)
    dark = client.get("/api/harmony/kits", params={"project_id": pid, "moods": "dark"}).json()
    assert dark and all("dark" in k["moods"] for k in dark)
    epic = next(k for k in kits if k["id"] == "epic_cinematic")
    verse = next(p for p in epic["parts"] if p["kind"] == "verse")
    assert (verse["chord_text"], verse["numerals"]) == ("Am*2 F*2 C*2 G*2", "i*2 VI*2 III*2 VII*2")


def test_apply_kit_fills_an_empty_song_with_a_full_form(client: TestClient) -> None:
    pid = _project(client)
    body = {"project_id": pid, "kit_id": "pop_lift", "names": {"verse": "Strofa"}}
    project = client.post("/api/harmony/kits/apply", json=body).json()
    names = {s["id"]: s["name"] for s in project["sections"]}
    assert [names[i] for i in project["arrangement"]] == [
        "Strofa",
        "Prechorus",
        "Chorus",
        "Strofa",
        "Prechorus",
        "Chorus",
        "Bridge",
        "Chorus",
        "Outro",
    ]
    chorus = next(s for s in project["sections"] if s["name"] == "Chorus")
    assert (chorus["chord_text"], chorus["bars"]) == ("C G Am F", 8)


def test_apply_kit_updates_matching_sections_and_appends_missing(client: TestClient) -> None:
    pid = _project(client)
    verse = client.post(f"/api/projects/{pid}/sections", json={"name": "Verse 1", "bars": 4})
    other = client.post(f"/api/projects/{pid}/sections", json={"name": "Drop", "bars": 4})
    body = {"project_id": pid, "kit_id": "folk_story", "create_missing": True}
    project = client.post("/api/harmony/kits/apply", json=body).json()
    sections = {s["name"]: s for s in project["sections"]}
    assert sections["Verse 1"]["chord_text"] == "C F C G"
    assert sections["Drop"]["chord_text"] == ""  # unknown kind: untouched
    assert project["arrangement"][:2] == [verse.json()["id"], other.json()["id"]]
    assert [sections_name for sections_name in sections] == [
        "Verse 1",
        "Drop",
        "Chorus",
        "Bridge",
        "Outro",
    ]
    only_update = {"project_id": pid, "kit_id": "pop_lift", "create_missing": False}
    again = client.post("/api/harmony/kits/apply", json=only_update).json()
    assert len(again["sections"]) == 5
    missing = client.post("/api/harmony/kits/apply", json={"project_id": pid, "kit_id": "nope"})
    assert missing.status_code == 404
