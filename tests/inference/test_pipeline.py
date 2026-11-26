"""End-to-end smoke test per model and role (CLAUDE.md section 9). Never asserts exact notes."""

import pytest

from app.core.harmony import parse_chord
from app.core.model import Key, Mode, Note, Role
from app.core.roles import role_spec
from app.core.timebase import bars_to_ticks
from app.gen.adapter import ContextTrack, GenerationSpec
from app.gen.engine import MidiGptEngine, generate_candidates

pytestmark = pytest.mark.inference
pytest.importorskip("midigpt.inference")

CHORDS = tuple(parse_chord(c) for c in ("Am", "F", "C", "G"))
CHORD_CONTEXT = ContextTrack(
    100,
    Role.CHORDS,
    0,
    tuple(
        Note(bar * 1920, p, 1900, 80)
        for bar, chord in enumerate(((57, 60, 64), (53, 57, 60), (55, 60, 64), (55, 59, 62)))
        for p in chord
    ),
)


@pytest.fixture(scope="module", params=["yellow_medium", "prism_medium"])
def engine(request: pytest.FixtureRequest) -> MidiGptEngine:
    return MidiGptEngine(request.param, device="cpu")


def test_raw_output_respects_pitch_mask(engine: MidiGptEngine) -> None:
    """Regression: scale and role range must constrain the model itself (before post-processing)."""
    spec = GenerationSpec(
        bars=4,
        target_role=Role.BASS,
        target_spec=role_spec(Role.BASS),
        target_program=33,
        context=(CHORD_CONTEXT,),
        key=Key(9, Mode.MINOR),
        chords=CHORDS,
        n_candidates=2,
        seed=7,
    )
    scale = {0, 2, 4, 5, 7, 9, 11}
    for candidate in engine.sample(spec):
        assert candidate.notes
        assert all(n.p % 12 in scale for n in candidate.notes)
        assert all(28 <= n.p <= 55 for n in candidate.notes)


@pytest.mark.parametrize("role", [Role.DRUMS, Role.BASS, Role.CHORDS, Role.PAD, Role.LEAD])
def test_generates_valid_part(engine: MidiGptEngine, role: Role) -> None:
    spec = GenerationSpec(
        bars=4,
        target_role=role,
        target_spec=role_spec(role),
        target_program=role_spec(role).program,
        context=() if role is Role.CHORDS else (CHORD_CONTEXT,),
        bpm=100,
        key=Key(9, Mode.MINOR),
        genre="pop",
        chords=CHORDS,
        density=5 if role is Role.DRUMS else None,
        n_candidates=2,
        seed=42,
    )
    ranked = generate_candidates(engine, spec)
    assert len(ranked) == 2
    best = ranked[0]
    assert best.rejected is None, best.rejected
    clip = bars_to_ticks(4)
    for note in best.notes:
        assert 0 <= note.t < note.end <= clip
        if role is not Role.DRUMS:
            assert spec.target_spec.low <= note.p <= spec.target_spec.high
    assert 0.0 <= best.score <= 1.0
