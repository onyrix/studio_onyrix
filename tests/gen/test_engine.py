import threading

import pytest

from app.core.harmony import parse_chord
from app.core.model import Note, Role
from app.core.progression import bar_spans
from app.core.roles import role_spec
from app.gen.adapter import ContextTrack, GenerationSpec
from app.gen.engine import (
    GenerationCancelled,
    RawCandidate,
    generate_candidates,
    rank_candidates,
    scoring_context,
)
from tests.fakes import FakeEngine


def spec(**kw: object) -> GenerationSpec:
    defaults: dict[str, object] = {
        "bars": 2,
        "target_role": Role.BASS,
        "target_spec": role_spec(Role.BASS),
        "target_program": 33,
        "chords": bar_spans([parse_chord("Am"), parse_chord("F")]),
        "seed": 100,
    }
    defaults.update(kw)
    return GenerationSpec(**defaults)  # type: ignore[arg-type]


def test_rank_puts_best_first_and_rejects_empty() -> None:
    good = tuple(Note(b * 480, 33 if b < 4 else 41, 480, 100) for b in range(8))
    bad = tuple(Note(b * 480, 34, 480, 100) for b in range(8))
    ranked = rank_candidates(
        spec(),
        [
            RawCandidate(1, bad),
            RawCandidate(2, ()),
            RawCandidate(3, good),
            RawCandidate(4, (), "boom"),
        ],
    )
    assert [c.seed for c in ranked] == [3, 1, 2, 4]
    assert ranked[0].score > ranked[1].score
    assert ranked[2].rejected == "empty"
    assert ranked[3].rejected == "error: boom"


def test_candidates_are_post_processed() -> None:
    raw = (Note(10, 70, 100, 100), Note(5, 20, 50, 100))  # off grid, out of range, overlapping
    best = rank_candidates(spec(), [RawCandidate(1, raw)])[0]
    assert all(n.t % 120 == 0 and 28 <= n.p <= 55 for n in best.notes)
    assert len(best.notes) == 1


def test_four_on_floor_drums_without_downbeat_kick_are_rejected() -> None:
    drum_spec = spec(
        target_role=Role.DRUMS, target_spec=role_spec(Role.DRUMS), genre="dance-electronic"
    )
    no_kick = tuple(Note(b * 480, 42, 120, 90) for b in range(8))
    assert rank_candidates(drum_spec, [RawCandidate(1, no_kick)])[0].rejected == (
        "missing downbeat kick"
    )


def test_scoring_context_collects_kicks_from_drum_context() -> None:
    ctx_track = ContextTrack(1, Role.DRUMS, 0, (Note(0, 36, 120, 100), Note(480, 38, 120, 100)))
    ctx = scoring_context(spec(context=(ctx_track,)))
    assert ctx.kick_onsets == frozenset({0})


def test_generate_is_reproducible_with_same_seed() -> None:
    a = generate_candidates(FakeEngine(), spec(n_candidates=4))
    b = generate_candidates(FakeEngine(), spec(n_candidates=4))
    assert len(a) == 4
    assert [(c.seed, c.notes) for c in a] == [(c.seed, c.notes) for c in b]
    assert {c.seed for c in a} == {100, 101, 102, 103}


def test_generate_cancelled() -> None:
    cancel = threading.Event()
    cancel.set()
    with pytest.raises(GenerationCancelled):
        generate_candidates(FakeEngine(), spec(), cancel=cancel)


def test_progress_reports_each_candidate() -> None:
    events: list[tuple[str, dict[str, object]]] = []
    generate_candidates(
        FakeEngine(), spec(n_candidates=3), progress=lambda e, d: events.append((e, d))
    )
    assert [e for e, _ in events] == ["sampling", "candidate", "candidate", "candidate"]


def test_rank_scores_before_the_harmonic_snap_and_keeps_snapped_notes() -> None:
    off_chord = tuple(Note(b * 480, 34, 480, 100) for b in range(8))  # A# on every beat
    ranked = rank_candidates(spec(), [RawCandidate(1, off_chord)])
    best = ranked[0]
    assert best.breakdown is not None and best.breakdown.ct == 0.0  # the model missed the chords
    chords = spec().chords
    assert all(n.p % 12 in chords[n.t // 1920].chord.pitch_class_set for n in best.notes)

    raw = rank_candidates(spec(harmony="off"), [RawCandidate(1, off_chord)])[0]
    assert {n.p for n in raw.notes} == {34}
