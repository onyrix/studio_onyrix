from hypothesis import given, settings
from hypothesis import strategies as st

from app.core.model import Note, Role
from app.core.postprocess import clamp_pitch, humanize, next_grid_point, postprocess, snap
from app.core.roles import role_spec
from app.core.scorer import overlap_ratio

CLIP = 4 * 1920

notes_strategy = st.lists(
    st.builds(
        Note,
        t=st.integers(0, CLIP + 500),
        p=st.integers(0, 127),
        d=st.integers(1, 3000),
        v=st.integers(1, 127),
    ),
    max_size=60,
)
roles = st.sampled_from(list(Role))


def test_snap_and_next_grid_point() -> None:
    assert snap(59) == 0
    assert snap(60) == 0  # tie -> earlier
    assert snap(61) == 120
    assert snap(150, triplets=True) == 160
    assert next_grid_point(120) == 240
    assert next_grid_point(120, triplets=True) == 160


def test_clamp_pitch() -> None:
    assert clamp_pitch(20, 28, 55) == 32
    assert clamp_pitch(70, 28, 55) == 46
    assert clamp_pitch(60, 60, 64) == 60
    assert 60 <= clamp_pitch(70, 60, 64) <= 64  # range narrower than an octave


def test_mono_bass_keeps_lowest_and_trims() -> None:
    spec = role_spec(Role.BASS)
    out = postprocess(
        [Note(0, 45, 960, 90), Note(0, 40, 480, 90), Note(240, 43, 240, 90)], spec, CLIP
    )
    assert out == (Note(0, 40, 240, 90), Note(240, 43, 240, 90))


def test_trims_at_clip_end_and_drops_after() -> None:
    spec = role_spec(Role.PAD)
    out = postprocess([Note(CLIP - 120, 60, 960, 80), Note(CLIP, 62, 120, 80)], spec, CLIP)
    assert out == (Note(CLIP - 120, 60, 120, 80),)


@settings(max_examples=200, deadline=None)
@given(notes_strategy, roles, st.booleans())
def test_postprocess_properties(notes: list[Note], role: Role, triplets: bool) -> None:
    spec = role_spec(role)
    once = postprocess(notes, spec, CLIP, triplets)
    assert postprocess(once, spec, CLIP, triplets) == once  # idempotent
    assert overlap_ratio(once, spec.monophonic) == 0.0  # no illegal overlaps
    for note in once:
        assert 0 <= note.t < note.end <= CLIP
        assert snap(note.t, triplets) == note.t
        assert snap(note.end, triplets) == note.end or note.end == CLIP
        if not spec.is_drum:
            assert spec.low <= note.p <= spec.high
    onsets = [n.t for n in once]
    assert max((onsets.count(t) for t in onsets), default=0) <= spec.max_polyphony


@given(notes_strategy, st.integers(0, 2**31))
def test_humanize_is_seeded_and_in_clip(notes: list[Note], seed: int) -> None:
    clean = postprocess(notes, role_spec(Role.LEAD), CLIP)
    a = humanize(clean, seed, CLIP)
    assert a == humanize(clean, seed, CLIP)
    assert all(0 <= n.t < n.end <= CLIP for n in a)
