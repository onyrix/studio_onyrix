import io
from typing import Any

import mido
from fastapi.testclient import TestClient

from tests.api.conftest import read_events


def fill(
    client: TestClient, project: dict[str, Any], role: str, notes: list[dict[str, int]]
) -> int:
    """Generate a clip (to create it), then set its notes manually."""
    body = {"section_id": project["section"]["id"], "track_id": project["tracks"][role]["id"]}
    job = client.post("/api/generate", json={**body, "seed": 1}).json()["id"]
    clip_id: int = read_events(client, job)[-1][1]["clip_id"]
    client.patch(f"/api/clips/{clip_id}", json={"notes": notes})
    return clip_id


def test_export_project_over_repeated_arrangement(
    client: TestClient, project: dict[str, Any]
) -> None:
    fill(client, project, "bass", [{"t": 0, "p": 33, "d": 480, "v": 100}])
    fill(client, project, "drums", [{"t": 480, "p": 38, "d": 120, "v": 90}])
    verse = project["section"]["id"]
    client.put(f"/api/projects/{project['id']}/arrangement", json={"section_ids": [verse, verse]})

    response = client.get(f"/api/export/project/{project['id']}.mid")
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/midi"
    assert 'filename="Demo.mid"' in response.headers["content-disposition"]

    mid = mido.MidiFile(file=io.BytesIO(response.content))
    assert mid.ticks_per_beat == 480
    names = [next(m.name for m in t if m.type == "track_name") for t in mid.tracks]
    assert names == ["Demo", "Drums", "Bass", "Lead"]

    def onsets(track: mido.MidiTrack) -> list[tuple[int, int]]:
        now, out = 0, []
        for msg in track:
            now += msg.time
            if msg.type == "note_on":
                out.append((now, msg.note))
        return out

    assert onsets(mid.tracks[2]) == [(0, 33), (4 * 1920, 33)]  # bass, second instance offset
    assert onsets(mid.tracks[1]) == [(480, 38), (4 * 1920 + 480, 38)]
    assert onsets(mid.tracks[3]) == []  # empty lead track still exported


def test_export_single_track(client: TestClient, project: dict[str, Any]) -> None:
    fill(client, project, "bass", [{"t": 0, "p": 33, "d": 480, "v": 100}])
    track_id = project["tracks"]["bass"]["id"]
    mid = mido.MidiFile(file=io.BytesIO(client.get(f"/api/export/track/{track_id}.mid").content))
    assert len(mid.tracks) == 2
    assert [m.program for m in mid.tracks[1] if m.type == "program_change"] == [33]
    assert client.get("/api/export/track/999.mid").status_code == 404


def test_project_clips_endpoint(client: TestClient, project: dict[str, Any]) -> None:
    clip_id = fill(client, project, "bass", [{"t": 0, "p": 33, "d": 480, "v": 100}])
    clips = client.get(f"/api/projects/{project['id']}/clips").json()
    assert [c["id"] for c in clips] == [clip_id]
    assert clips[0]["current_version"]["notes"] == [{"t": 0, "p": 33, "d": 480, "v": 100}]
