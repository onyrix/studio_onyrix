import pytest

from app.core.harmony import parse_chord
from app.core.model import Key, Mode, Note, Role
from app.core.roles import role_spec
from app.gen.adapter import (
    ContextTrack,
    GenerationSpec,
    ModelCaps,
    build_request,
    build_score,
    choose_window,
    extract_notes,
    key_signature_index,
    pitch_mask_for_bar,
)

pytest.importorskip("midigpt")

# Capabilities as reported at runtime in M1 (docs/midigpt-notes.md).
YELLOW = ModelCaps(
    name="yellow_medium",
    num_bars_map=(4, 8),
    attribute_sizes={"note_density": 10, "max_polyphony": 10, "min_polyphony": 10},
    attribute_levels={"note_density": "track", "max_polyphony": "track", "min_polyphony": "track"},
    attribute_track_types={
        "note_density": "drum",
        "max_polyphony": "melodic",
        "min_polyphony": "melodic",
    },
)
PRISM = ModelCaps(
    name="prism_medium",
    num_bars_map=(4, 8, 12, 16),
    attribute_sizes={"key_signature": 25, "bar_max_polyphony": 10, "bar_note_density": 10},
    attribute_levels={
        "key_signature": "track",
        "bar_max_polyphony": "bar",
        "bar_note_density": "bar",
    },
    attribute_track_types={
        "key_signature": "melodic",
        "bar_max_polyphony": "melodic",
        "bar_note_density": "drum",
    },
    genres=("jazz", "dance-electronic"),
)

CHORDS = tuple(parse_chord(c) for c in ("Am", "F", "C", "G"))


def bass_spec(**kw: object) -> GenerationSpec:
    defaults: dict[str, object] = {
        "bars": 4,
        "target_role": Role.BASS,
        "target_spec": role_spec(Role.BASS),
        "target_program": 33,
        "chords": CHORDS,
        "key": Key(9, Mode.MINOR),
        "seed": 11,
        "context": (
            ContextTrack(1, Role.DRUMS, 0, (Note(0, 36, 120, 100), Note(1920 + 480, 38, 120, 90))),
        ),
    }
    defaults.update(kw)
    return GenerationSpec(**defaults)  # type: ignore[arg-type]


def test_key_index_and_window() -> None:
    assert key_signature_index(Key(9, Mode.MINOR)) == 21
    assert key_signature_index(Key(2, Mode.MAJOR)) == 2
    assert choose_window(4, (4, 8)) == 4
    assert choose_window(6, (4, 8, 12, 16)) == 8
    assert choose_window(32, (4, 8)) == 8


def test_build_score_splits_bars_relative() -> None:
    score, target = build_score(bass_spec())
    assert target == 1
    assert len(score.tracks) == 2 and score.resolution == 480 and score.tempo == 500000
    drums = score.tracks[0]
    assert drums.track_type == "drum"
    assert [(n.pitch, n.onset_ticks) for n in drums.bars[1].notes] == [(38, 480)]
    assert all(not bar.notes for bar in score.tracks[1].bars)
    assert score.tracks[1].instrument == 33


def test_pitch_mask_uses_chord_for_bass_and_scale_for_lead() -> None:
    bass = pitch_mask_for_bar(bass_spec(), 1)
    assert bass["pitch_classes"] == sorted(parse_chord("F").pitch_class_set)
    assert bass["shape"] == {"type": "uniform", "min": 28, "max": 55}
    lead = pitch_mask_for_bar(bass_spec(target_role=Role.LEAD, target_spec=role_spec(Role.LEAD)), 1)
    assert lead["pitch_classes"] == [0, 2, 4, 5, 7, 9, 11]  # A minor scale


def test_request_for_prism_uses_bar_attributes_key_and_genre() -> None:
    request = build_request(bass_spec(genre="Jazz"), 1, PRISM)
    target = request.tracks[1]
    assert target.bars == [0, 1, 2, 3]
    assert target.attributes == {"key_signature": 21}
    assert target.bar_attributes[0] == {"bar_max_polyphony": 0}
    assert "pitch_mask" in target.bar_controls[3]
    assert request.tracks[0].bars == []
    assert request.controls == {"genre": "jazz"}
    assert request.config.seed == 11 and request.config.num_candidates == 4
    assert request.config.mask_mode == "attention" and request.config.top_p == 0.95


def test_request_for_yellow_uses_only_supported_attributes() -> None:
    request = build_request(bass_spec(genre="jazz"), 1, YELLOW)
    target = request.tracks[1]
    assert target.attributes == {"max_polyphony": 0}
    assert target.bar_attributes == {}
    assert request.controls == {}


def test_drum_density_mapping() -> None:
    spec = bass_spec(target_role=Role.DRUMS, target_spec=role_spec(Role.DRUMS), density=7)
    assert build_request(spec, 1, YELLOW).tracks[1].attributes == {"note_density": 7}
    prism_target = build_request(spec, 1, PRISM).tracks[1]
    assert prism_target.bar_attributes[2] == {"bar_note_density": 7}
    assert prism_target.bar_controls == {}


def test_extract_notes_resamples_and_flattens() -> None:
    from midigpt import Bar, Score, Track
    from midigpt import Note as MNote

    score = Score(
        tracks=[Track(bars=[Bar([MNote(40, 0, 0, 160)]), Bar([MNote(43, 90, 1920, 480)])])],
        resolution=1920,
    )
    assert extract_notes(score, 0, bass_spec().ts) == (
        Note(0, 40, 40, 1),
        Note(1920 + 480, 43, 120, 90),
    )
