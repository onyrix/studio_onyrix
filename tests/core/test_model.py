import pytest

from app.core.model import ChordSlot, Clip, Key, Note, Role, Section


def test_note_round_trip_dict() -> None:
    note = Note(t=120, p=60, d=240, v=100)
    assert note.end == 360
    assert Note.from_dict(note.to_dict()) == note


@pytest.mark.parametrize(
    "kwargs",
    [
        {"t": -1, "p": 60, "d": 1, "v": 1},
        {"t": 0, "p": 128, "d": 1, "v": 1},
        {"t": 0, "p": 60, "d": 0, "v": 1},
        {"t": 0, "p": 60, "d": 1, "v": 0},
        {"t": 0, "p": 60, "d": 1, "v": 128},
    ],
)
def test_note_rejects_invalid_values(kwargs: dict[str, int]) -> None:
    with pytest.raises(ValueError):
        Note(**kwargs)


def test_clip_length() -> None:
    assert Clip(bars=4).length_ticks() == 4 * 1920
    with pytest.raises(ValueError):
        Clip(bars=0)


def test_key_and_chord_validation() -> None:
    Key(tonic=9)
    ChordSlot(root=0, quality="maj7", pitch_class_set=frozenset({0, 4, 7, 11}))
    with pytest.raises(ValueError):
        Key(tonic=12)
    with pytest.raises(ValueError):
        ChordSlot(root=0, quality="", pitch_class_set=frozenset({12}))


def test_section_slots_default_empty() -> None:
    section = Section(name="verse", bars=8)
    assert section.slots == {}
    with pytest.raises(ValueError):
        Section(name="x", bars=0)


def test_role_values() -> None:
    assert {r.value for r in Role} == {"drums", "bass", "chords", "pad", "lead", "other"}
