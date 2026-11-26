import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.core.harmony import parse_chord
from app.core.model import Note, Role
from app.core.postprocess import HARMONY_LEVELS, harmonic_snap, postprocess
from app.core.progression import ChordSpan, bar_spans, chord_timeline, parse_progression
from app.core.roles import role_spec

BAR = 1920
BARS = 4
CLIP = BARS * BAR
AM_F_C_G_LIST = [parse_chord(c) for c in ("Am", "F", "C", "G")]
AM_F_C_G = bar_spans(AM_F_C_G_LIST)

notes_strategy = st.lists(
    st.builds(
        Note,
        t=st.integers(0, CLIP - 1),
        p=st.integers(0, 127),
        d=st.integers(1, 3000),
        v=st.integers(1, 127),
    ),
    max_size=40,
)
melodic = st.sampled_from([Role.BASS, Role.CHORDS, Role.PAD, Role.LEAD, Role.OTHER])
grids = st.lists(st.one_of(st.none(), st.sampled_from(AM_F_C_G_LIST)), min_size=1, max_size=4).map(
    bar_spans
)


def _pipeline(notes: list[Note], role: Role, grid: tuple[ChordSpan, ...], level: str) -> tuple:
    spec = role_spec(role)
    clean = postprocess(notes, spec, CLIP)
    return postprocess(harmonic_snap(clean, grid, spec, CLIP, level=level), spec, CLIP)


@given(notes_strategy, melodic, grids, st.sampled_from(HARMONY_LEVELS))
def test_snap_is_idempotent_and_keeps_range(
    notes: list[Note], role: Role, grid: tuple[ChordSpan, ...], level: str
) -> None:
    spec = role_spec(role)
    once = _pipeline(notes, role, grid, level)
    assert _pipeline(list(once), role, grid, level) == once
    assert all(spec.low <= n.p <= spec.high for n in once)
    assert all(0 <= n.t < n.end <= CLIP for n in once)


@given(notes_strategy, st.sampled_from([Role.BASS, Role.LEAD]))
def test_beats_of_mono_roles_are_chord_tones(notes: list[Note], role: Role) -> None:
    out = _pipeline(notes, role, AM_F_C_G, "normal")
    for note in out:
        if note.t % 480 == 0:
            assert note.p % 12 in AM_F_C_G_LIST[note.t // BAR].pitch_class_set


@given(notes_strategy, st.sampled_from([Role.CHORDS, Role.PAD]))
def test_polyphonic_roles_are_all_chord_tones(notes: list[Note], role: Role) -> None:
    for note in _pipeline(notes, role, AM_F_C_G, "normal"):
        assert note.p % 12 in AM_F_C_G_LIST[note.t // BAR].pitch_class_set


@given(notes_strategy)
def test_off_and_drums_are_untouched(notes: list[Note]) -> None:
    lead = role_spec(Role.LEAD)
    assert harmonic_snap(notes, AM_F_C_G, lead, CLIP, level="off") == tuple(notes)
    drums = role_spec(Role.DRUMS)
    assert harmonic_snap(notes, AM_F_C_G, drums, CLIP, level="strict") == tuple(notes)
    assert harmonic_snap(notes, (), lead, CLIP) == tuple(notes)


def test_bass_downbeat_goes_to_the_root() -> None:
    bass = role_spec(Role.BASS)
    # E on the downbeat of an Am bar is a chord tone, but the bass plays the root A.
    out = harmonic_snap([Note(0, 40, 480, 90)], AM_F_C_G, bass, CLIP)
    assert out[0].p % 12 == 9
    kept = harmonic_snap([Note(0, 40, 480, 90)], AM_F_C_G, bass, CLIP, bass_root=False)
    assert kept[0].p == 40


def test_nearest_chord_tone_ties_go_down() -> None:
    lead = role_spec(Role.LEAD)
    # D (62) over C major: C (60) and E (64) are both 2 semitones away.
    out = harmonic_snap([Note(0, 62, 480, 90)], bar_spans([parse_chord("C")]), lead, BAR)
    assert out[0].p == 60


def test_offbeats_of_mono_roles_are_passing_tones() -> None:
    lead = role_spec(Role.LEAD)
    passing = Note(240, 62, 240, 90)  # D on the "and" of beat 1 over Am
    assert harmonic_snap([passing], AM_F_C_G, lead, CLIP)[0] == passing
    assert harmonic_snap([passing], AM_F_C_G, lead, CLIP, level="strict")[0].p % 12 in {9, 0, 4}


def test_light_only_touches_downbeats() -> None:
    lead = role_spec(Role.LEAD)
    notes = [Note(0, 62, 480, 90), Note(480, 62, 480, 90)]
    out = harmonic_snap(notes, AM_F_C_G, lead, CLIP, level="light")
    assert out[0].p != 62
    assert out[1].p == 62


def test_held_note_is_trimmed_at_a_chord_change_that_excludes_it() -> None:
    pad = role_spec(Role.PAD)
    held_a = Note(0, 57 + 12, 2 * BAR, 90)  # A held from Am into F: A is in F, keeps sounding
    held_e = Note(0, 64, 2 * BAR, 90)  # E held from Am into F: E is not in F, trimmed
    out = harmonic_snap([held_a, held_e], AM_F_C_G, pad, CLIP)
    assert out[0].end == 2 * BAR
    assert out[1].end == BAR
    light = harmonic_snap([held_e], AM_F_C_G, pad, CLIP, level="light")
    assert light[0].end == 2 * BAR


def test_unknown_level() -> None:
    with pytest.raises(ValueError):
        harmonic_snap([], AM_F_C_G, role_spec(Role.LEAD), CLIP, level="loud")


def test_split_bar_snaps_at_each_chord_start() -> None:
    spans = chord_timeline(parse_progression("(Am F)"), bars=1)
    bass = role_spec(Role.BASS)
    # B (47) on beat 3 of a bar split Am | F: the F chord starts there, so the bass plays F.
    out = harmonic_snap([Note(960, 47, 480, 90)], spans, bass, BAR)
    assert out[0].p % 12 == 5
    lead = role_spec(Role.LEAD)
    held = harmonic_snap([Note(0, 64, BAR, 90)], spans, lead, BAR)  # E is not in F
    assert held[0].end == 960


def test_long_chord_does_not_restart_at_the_next_bar_for_light() -> None:
    spans = chord_timeline(parse_progression("C*2"), bars=2)
    lead = role_spec(Role.LEAD)
    # Bar 2 downbeat inside a two-bar C chord still counts as a chord start for "light".
    out = harmonic_snap([Note(BAR, 62, 480, 90)], spans, lead, 2 * BAR, level="light")
    assert out[0].p % 12 in {0, 4, 7}
