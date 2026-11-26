import pytest

from app.core import drums
from app.core.harmony import parse_chord
from app.core.model import Note, Role
from app.core.progression import bar_spans
from app.core.roles import role_spec
from app.core.scorer import ScoringContext, hard_constraint_violation, score_notes

AM_F = bar_spans([parse_chord("Am"), parse_chord("F")])


def bass_ctx(**kw: object) -> ScoringContext:
    defaults: dict[str, object] = {"spec": role_spec(Role.BASS), "bars": 2, "chords": AM_F}
    defaults.update(kw)
    return ScoringContext(**defaults)  # type: ignore[arg-type]


def roots_on_beats() -> list[Note]:
    return [Note(b * 480, 33, 480, 100) for b in range(4)] + [
        Note(1920 + b * 480, 41, 480, 100) for b in range(4)
    ]


def test_perfect_bass_scores_one() -> None:
    kicks = frozenset(n.t for n in roots_on_beats())
    result = score_notes(roots_on_beats(), bass_ctx(kick_onsets=kicks))
    assert result.total == pytest.approx(1.0)
    assert (result.ct, result.r, result.d, result.o, result.k) == (1.0, 1.0, 1.0, 0.0, 1.0)


def test_wrong_notes_lower_ct_and_kick_alignment() -> None:
    notes = [Note(b * 480, 34, 480, 100) for b in range(8)]  # Bb: not in Am nor F
    result = score_notes(notes, bass_ctx(kick_onsets=frozenset({0})))
    assert result.ct == 0.0
    assert result.k == pytest.approx(1 / 8)
    assert result.total < 0.6


def test_density_term() -> None:
    sparse = [Note(0, 33, 480, 100)]
    assert score_notes(sparse, bass_ctx()).d == pytest.approx(1 - 3.5 / 4)


def test_overlaps_counted_on_raw_notes() -> None:
    notes = [Note(0, 33, 960, 100), Note(480, 36, 480, 100)]
    assert score_notes(notes, bass_ctx()).o == 1.0


def test_no_harmony_is_neutral() -> None:
    ctx = ScoringContext(spec=role_spec(Role.LEAD), bars=1)
    assert score_notes([Note(0, 70, 480, 90)], ctx).ct == 1.0


def test_drums_use_pattern_coverage_and_hard_constraint() -> None:
    spec = role_spec(Role.DRUMS)
    ctx = ScoringContext(spec=spec, bars=1, four_on_floor=True)
    good = [Note(b * 480, drums.KICK, 120, 100) for b in range(4)] + [
        Note(b * 480, drums.SNARE, 120, 100) for b in (1, 3)
    ]
    assert score_notes(good, ctx).ct == 1.0
    assert hard_constraint_violation(good, ctx) is None
    assert hard_constraint_violation(good[1:], ctx) == "missing downbeat kick"
    assert hard_constraint_violation([], ctx) == "empty"
