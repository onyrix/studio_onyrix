"""Project <-> midigpt Score conversion and request building.

Field names verified in M1 (docs/midigpt-notes.md). midigpt is imported lazily so that the app
and the pure tests never need it at import time. Controls are derived from the capabilities the
loaded model reports at runtime (`ModelCaps`), never hard-coded.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from app.core.harmony import scale_pitch_classes
from app.core.model import Key, Mode, Note, Role
from app.core.progression import ChordSpan, chords_in_bar
from app.core.roles import RoleSpec
from app.core.timebase import FOUR_FOUR, PPQ, TimeSignature, bar_ticks, bpm_to_us_per_quarter


@dataclass(frozen=True)
class ContextTrack:
    track_id: int
    role: Role
    program: int
    notes: tuple[Note, ...]  # clip-relative ticks over the section


@dataclass(frozen=True)
class GenerationSpec:
    """Everything needed to generate one part of one section. Pure data."""

    bars: int
    target_role: Role
    target_spec: RoleSpec
    target_program: int
    context: tuple[ContextTrack, ...] = ()
    bpm: float = 120.0
    ts: TimeSignature = FOUR_FOUR
    key: Key | None = None
    genre: str = ""
    chords: tuple[ChordSpan, ...] = ()  # chord timeline over the section (clip-relative ticks)
    density: int | None = None  # 0 (sparsest) .. 9 (densest); drums only on current models
    n_candidates: int = 4
    seed: int = 0
    temperature: float = 1.0
    top_p: float = 0.95
    harmony: str = "normal"  # harmonic snap level, see core.postprocess.HARMONY_LEVELS


@dataclass(frozen=True)
class ModelCaps:
    """What a loaded checkpoint supports, read at runtime."""

    name: str
    num_bars_map: tuple[int, ...]
    attribute_sizes: dict[str, int] = field(default_factory=dict)
    attribute_levels: dict[str, str] = field(default_factory=dict)
    attribute_track_types: dict[str, str] = field(default_factory=dict)
    genres: tuple[str, ...] = ()
    max_context_tokens: int = 0

    def has(self, name: str, level: str, track_type: str) -> bool:
        return (
            name in self.attribute_sizes
            and self.attribute_levels.get(name) == level
            and self.attribute_track_types.get(name) in (track_type, "both")
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "model": self.name,
            "num_bars_map": list(self.num_bars_map),
            "attribute_sizes": self.attribute_sizes,
            "attribute_levels": self.attribute_levels,
            "attribute_track_types": self.attribute_track_types,
            "genres": list(self.genres),
            "max_context_tokens": self.max_context_tokens,
        }


def key_signature_index(key: Key) -> int:
    """midigpt KeySignature encoding: 0-11 major (tonic), 12-23 minor, 24 = none."""
    return key.tonic + (12 if key.mode is Mode.MINOR else 0)


def choose_window(bars: int, num_bars_map: Sequence[int]) -> int:
    """Smallest model window covering `bars`, else the largest (the library windows the rest)."""
    windows = sorted(num_bars_map) or [4]
    return next((w for w in windows if w >= bars), windows[-1])


def split_into_bars(notes: Sequence[Note], bars: int, ts: TimeSignature) -> list[list[Note]]:
    out: list[list[Note]] = [[] for _ in range(bars)]
    length = bar_ticks(ts)
    for note in notes:
        bar = note.t // length
        if 0 <= bar < bars:
            out[bar].append(note)
    return out


def build_score(spec: GenerationSpec) -> tuple[Any, int]:
    """Return (midigpt Score, index of the target track). The target is the last track."""
    from midigpt import Bar, Score, Track
    from midigpt import Note as MNote

    length = bar_ticks(spec.ts)

    def make_track(notes: Sequence[Note], program: int, role: Role) -> Any:
        bars = [
            Bar(
                notes=[MNote(n.p, n.v, n.t - i * length, n.d) for n in bar_notes],
                ts_numerator=spec.ts.numerator,
                ts_denominator=spec.ts.denominator,
            )
            for i, bar_notes in enumerate(split_into_bars(notes, spec.bars, spec.ts))
        ]
        return Track(
            bars=bars,
            instrument=program,
            track_type="drum" if role is Role.DRUMS else "melodic",
        )

    tracks = [make_track(c.notes, c.program, c.role) for c in spec.context]
    tracks.append(make_track((), spec.target_program, spec.target_role))
    score = Score(tracks=tracks, resolution=PPQ, tempo=bpm_to_us_per_quarter(spec.bpm))
    return score, len(tracks) - 1


def pitch_mask(spec: GenerationSpec) -> dict[str, Any]:
    """Track-level pitch mask: the key's scale (else the union of the chord tones) as hard pitch
    classes, plus the role range as a uniform shape.

    midigpt 0.4.2 honours `pitch_mask` only in track-level `controls`; inside `bar_controls` it
    passes validation but is ignored (only `time_signature` is read there). Chord-by-chord
    guidance therefore comes from context tracks and the scorer, not from the mask.
    """
    mask: dict[str, Any] = {
        "shape": {"type": "uniform", "min": spec.target_spec.low, "max": spec.target_spec.high}
    }
    if spec.key is not None:
        pcs = scale_pitch_classes(spec.key)
    else:
        pcs = frozenset().union(*(s.chord.pitch_class_set for s in spec.chords))
    if pcs:
        mask["pitch_classes"] = sorted(pcs)
    return mask


def _level(value: int, size: int) -> int:
    return max(0, min(size - 1, value))


def build_request(spec: GenerationSpec, target_index: int, caps: ModelCaps) -> Any:
    from midigpt.inference import GenerationRequest, InferenceConfig, TrackPrompt

    is_drum = spec.target_role is Role.DRUMS
    track_type = "drum" if is_drum else "melodic"
    bars = list(range(spec.bars))
    attributes: dict[str, int] = {}
    bar_attributes: dict[int, dict[str, int]] = {}
    track_controls: dict[str, Any] = {}

    def set_attr(names: tuple[str, str], value: int) -> None:
        bar_name, track_name = names
        if caps.has(bar_name, "bar", track_type):
            level = _level(value, caps.attribute_sizes[bar_name])
            for b in bars:
                bar_attributes.setdefault(b, {})[bar_name] = level
        elif caps.has(track_name, "track", track_type):
            attributes[track_name] = _level(value, caps.attribute_sizes[track_name])

    if not is_drum:
        if spec.key is not None and caps.has("key_signature", "track", track_type):
            attributes["key_signature"] = key_signature_index(spec.key)
        if spec.target_spec.monophonic:
            set_attr(("bar_max_polyphony", "max_polyphony"), 0)  # level 0 = "1 voice"
        # `pitch_class_set` is the COUNT of distinct pitch classes in a bar (B-70), not which
        # ones: for chord parts, ask for as many pitch classes as the bar's chords have.
        if spec.target_role in (Role.CHORDS, Role.PAD) and caps.has(
            "pitch_class_set", "bar", track_type
        ):
            size = caps.attribute_sizes["pitch_class_set"]
            for b in bars:
                in_bar = chords_in_bar(spec.chords, b, spec.ts)
                if in_bar:
                    count = len(frozenset().union(*(c.pitch_class_set for c in in_bar)))
                    bar_attributes.setdefault(b, {})["pitch_class_set"] = _level(count, size)
        track_controls["pitch_mask"] = pitch_mask(spec)
    elif spec.density is not None:
        set_attr(("bar_note_density", "note_density"), spec.density)

    prompts = [TrackPrompt(id=i, bars=[]) for i in range(target_index)]
    # The target track is always empty (built by `build_score`), so it is generated from scratch:
    # `autoregressive=True`. Infill on an empty track degenerates into one repeated pitch class
    # per bar (B-70 finding, docs/midigpt-notes.md).
    prompts.append(
        TrackPrompt(
            id=target_index,
            bars=bars,
            autoregressive=True,
            attributes=attributes,
            bar_attributes=bar_attributes,
            controls=track_controls,
        )
    )
    controls: dict[str, Any] = {}
    genre = spec.genre.strip().lower()
    if genre and genre in caps.genres:
        controls["genre"] = genre

    config = InferenceConfig(
        seed=spec.seed,
        temperature=spec.temperature,
        top_p=spec.top_p,
        mask_mode="attention",
        model_dim=choose_window(spec.bars, caps.num_bars_map),
        num_candidates=spec.n_candidates,
    )
    return GenerationRequest(tracks=prompts, config=config, controls=controls)


def extract_notes(score: Any, track_index: int, ts: TimeSignature) -> tuple[Note, ...]:
    """Notes of one track as clip-relative ticks at PPQ 480 (decoded scores come back at 1920)."""
    if score.resolution != PPQ:
        score = score.resample(PPQ)
    length = bar_ticks(ts)
    out = []
    for i, bar in enumerate(score.tracks[track_index].bars):
        for n in bar.notes:
            out.append(
                Note(
                    t=max(0, i * length + int(n.onset_ticks)),
                    p=min(max(int(n.pitch), 0), 127),
                    d=max(1, int(n.duration_ticks)),
                    v=min(max(int(n.velocity), 1), 127),
                )
            )
    return tuple(sorted(out, key=lambda n: (n.t, n.p)))
