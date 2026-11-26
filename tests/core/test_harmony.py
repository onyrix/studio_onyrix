import pytest

from app.core.harmony import (
    chord_slot_from_dict,
    chord_slot_to_dict,
    parse_chord,
    scale_pitch_classes,
)
from app.core.model import Key, Mode


@pytest.mark.parametrize(
    ("symbol", "root", "pcs"),
    [
        ("C", 0, {0, 4, 7}),
        ("Am", 9, {9, 0, 4}),
        ("F#m7b5", 6, {6, 9, 0, 4}),
        ("Bbmaj7", 10, {10, 2, 5, 9}),
        ("Ebm9", 3, {3, 6, 10, 1, 5}),
        ("Gsus4", 7, {7, 0, 2}),
        ("C/E", 0, {0, 4, 7}),
        ("Am/G", 9, {9, 0, 4, 7}),
        ("Dmin7", 2, {2, 5, 9, 0}),
    ],
)
def test_parse_chord(symbol: str, root: int, pcs: set[int]) -> None:
    slot = parse_chord(symbol)
    assert slot.root == root
    assert slot.pitch_class_set == frozenset(pcs)


@pytest.mark.parametrize("bad", ["", "H", "Cxyz", "c", "C#/"])
def test_parse_chord_rejects_unknown(bad: str) -> None:
    with pytest.raises(ValueError):
        parse_chord(bad)


def test_scales() -> None:
    assert scale_pitch_classes(Key(0, Mode.MAJOR)) == frozenset({0, 2, 4, 5, 7, 9, 11})
    assert scale_pitch_classes(Key(9, Mode.MINOR)) == frozenset({9, 11, 0, 2, 4, 5, 7})


def test_chord_slot_dict_round_trip() -> None:
    slot = parse_chord("Fmaj7")
    assert chord_slot_from_dict(chord_slot_to_dict(slot)) == slot
    assert chord_slot_from_dict({"root": 9, "quality": "m"}) == parse_chord("Am")
