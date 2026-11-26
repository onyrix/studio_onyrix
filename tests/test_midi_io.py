"""Golden test for .mid export. The golden file is a JSON description (rule 5: no .mid in git).

Regenerate after an intentional format change with: UPDATE_GOLDEN=1 pytest tests/test_midi_io.py
"""

import io
import json
import os
from pathlib import Path
from typing import Any

import mido

from app.core.model import Note
from app.core.timebase import TimeSignature
from app.midi_io import ExportTrack, build_midi, to_bytes

GOLDEN = Path(__file__).parent / "golden" / "export_basic.json"


def describe(mid: mido.MidiFile) -> dict[str, Any]:
    return {
        "type": mid.type,
        "ticks_per_beat": mid.ticks_per_beat,
        "tracks": [[str(msg) for msg in track] for track in mid.tracks],
    }


def sample_midi() -> mido.MidiFile:
    return build_midi(
        "Demo",
        100.0,
        TimeSignature(4, 4),
        [
            ExportTrack("Drums", 0, True, (Note(0, 36, 120, 110), Note(480, 38, 120, 90))),
            ExportTrack(
                "Bass",
                33,
                False,
                (Note(0, 33, 480, 100), Note(480, 33, 480, 100), Note(1920, 41, 960, 95)),
            ),
            ExportTrack("Pad", 89, False, (Note(0, 57, 1920, 70), Note(0, 60, 1920, 70))),
        ],
    )


def test_export_matches_golden() -> None:
    mid = mido.MidiFile(file=io.BytesIO(to_bytes(sample_midi())))  # through bytes, as served
    actual = describe(mid)
    if os.environ.get("UPDATE_GOLDEN"):
        GOLDEN.parent.mkdir(exist_ok=True)
        GOLDEN.write_text(json.dumps(actual, indent=2) + "\n", encoding="utf-8")
    assert actual == json.loads(GOLDEN.read_text(encoding="utf-8"))


def test_export_essentials() -> None:
    mid = mido.MidiFile(file=io.BytesIO(to_bytes(sample_midi())))
    assert mid.ticks_per_beat == 480
    conductor = mid.tracks[0]
    assert [m.tempo for m in conductor if m.type == "set_tempo"] == [600000]
    names = [next(m.name for m in t if m.type == "track_name") for t in mid.tracks]
    assert names == ["Demo", "Drums", "Bass", "Pad"]
    programs = [[m.program for m in t if m.type == "program_change"] for t in mid.tracks[1:]]
    assert programs == [[], [33], [89]]
    channels = [{m.channel for m in t if m.type == "note_on"} for t in mid.tracks[1:]]
    assert channels == [{9}, {0}, {1}]
    # Back-to-back notes of the same pitch: note_off is written before the next note_on.
    bass = [(m.type, m.time) for m in mid.tracks[2] if m.type in ("note_on", "note_off")]
    assert bass[:3] == [("note_on", 0), ("note_off", 480), ("note_on", 0)]
