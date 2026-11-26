from app.core import drums
from app.core.model import Note


def four_on_floor_bar(bars: int = 1) -> list[Note]:
    notes = []
    for bar in range(bars):
        base = bar * 1920
        notes += [Note(base + b * 480, drums.KICK, 120, 100) for b in range(4)]
        notes += [Note(base + b * 480, drums.CLAP, 120, 100) for b in (1, 3)]
    return notes


def test_grid_round_trip() -> None:
    notes = four_on_floor_bar()
    grid = drums.notes_to_grid(notes, bars=1)
    assert grid[drums.KICK] == [i % 4 == 0 for i in range(16)]
    assert set(drums.grid_to_notes(grid)) == {Note(n.t, n.p, 120, 100) for n in notes}


def test_pattern_coverage() -> None:
    assert drums.pattern_coverage(four_on_floor_bar(2), bars=2, four_on_floor=True) == 1.0
    only_kick_one = [Note(0, drums.KICK, 120, 100)]
    assert drums.pattern_coverage(only_kick_one, bars=1, four_on_floor=False) == 1 / 3
    assert drums.pattern_coverage(only_kick_one, bars=1, four_on_floor=True) == 1 / 6


def test_missing_downbeat_kick() -> None:
    assert not drums.missing_downbeat_kick(four_on_floor_bar(2), bars=2)
    assert drums.missing_downbeat_kick(four_on_floor_bar(1), bars=2)


def test_four_on_floor_genres() -> None:
    assert drums.is_four_on_floor("Dance-Electronic")
    assert not drums.is_four_on_floor("jazz")
    assert not drums.is_four_on_floor(None)
