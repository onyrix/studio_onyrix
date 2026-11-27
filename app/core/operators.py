"""Progression transformation operators for the harmonic explorer (B-58). Pure.

Each operator turns a progression (chord events with durations) into a variant. Chord
operators act on one chord (the one selected in the UI); progression operators act on all.
An operator that does not apply (e.g. a tritone substitute of a minor chord) raises
`NotApplicable`. Operators never change the total length of the progression, except the
harmonic-rhythm ones (`double_time`, `half_time`), which say so.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace

from app.core.harmony import QUALITIES, SCALES, diatonic_chords, make_chord
from app.core.model import ChordSlot, Key, Mode
from app.core.progression import ChordEvent
from app.core.timebase import FOUR_FOUR, TimeSignature


class NotApplicable(ValueError):
    """The operator does not apply to this chord or progression."""


@dataclass(frozen=True)
class Operator:
    id: str
    scope: str  # "chord" | "progression"
    apply: Callable[[list[ChordEvent], int, Key, TimeSignature], list[ChordEvent]]


def _beats(event: ChordEvent, ts: TimeSignature) -> int:
    return ts.numerator if event.beats is None else event.beats


def _with_beats(event: ChordEvent, beats: int, ts: TimeSignature) -> ChordEvent:
    return ChordEvent(event.chord, None if beats == ts.numerator else beats)


def _split(event: ChordEvent, ts: TimeSignature) -> tuple[int, int]:
    beats = _beats(event, ts)
    if beats < 2:
        raise NotApplicable("the chord is too short to split")
    return beats - beats // 2, beats // 2


def _is_major(chord: ChordSlot) -> bool:
    return chord.quality in ("", "7", "maj7", "6", "9", "maj9", "add9", "sus2", "sus4")


def _is_minor(chord: ChordSlot) -> bool:
    q = chord.quality
    return q.startswith("m") and not q.startswith("maj") and q != "m7b5"


def _replace_at(events: list[ChordEvent], i: int, chord: ChordSlot) -> list[ChordEvent]:
    if chord.pitch_class_set == events[i].chord.pitch_class_set:
        raise NotApplicable("no change")
    out = list(events)
    out[i] = replace(events[i], chord=chord)
    return out


def identify_chord(pcs: frozenset[int], prefer_root: int | None = None) -> ChordSlot | None:
    """A chord of our vocabulary with exactly these pitch classes (triads, then sevenths...)."""
    order = sorted(QUALITIES, key=lambda q: (len(QUALITIES[q]), q))
    roots = sorted(pcs, key=lambda r: (r != prefer_root, r))
    for quality in order:
        for root in roots:
            chord = make_chord(root, quality)
            if chord.pitch_class_set == pcs:
                return chord
    return None


# ---- chord operators ----------------------------------------------------------------------


def relative(events: list[ChordEvent], i: int, key: Key, ts: TimeSignature) -> list[ChordEvent]:
    chord = events[i].chord
    if _is_major(chord):
        return _replace_at(events, i, make_chord(chord.root + 9, "m"))
    if _is_minor(chord):
        return _replace_at(events, i, make_chord(chord.root + 3, ""))
    raise NotApplicable("only major and minor chords have a relative")


def borrow(events: list[ChordEvent], i: int, key: Key, ts: TimeSignature) -> list[ChordEvent]:
    """The chord on the same scale degree in the parallel mode (IV -> iv, vi -> bVI ...)."""
    chord = events[i].chord
    scale = [(key.tonic + s) % 12 for s in SCALES[key.mode]]
    if chord.root not in scale:
        raise NotApplicable("the chord is not on a degree of the key")
    degree = scale.index(chord.root)
    other = Key(key.tonic, Mode.MINOR if key.mode is Mode.MAJOR else Mode.MAJOR)
    return _replace_at(events, i, diatonic_chords(other)[degree])


def tritone_sub(events: list[ChordEvent], i: int, key: Key, ts: TimeSignature) -> list[ChordEvent]:
    chord = events[i].chord
    if chord.quality not in ("", "7", "9"):
        raise NotApplicable("only dominant (major or 7) chords have a tritone substitute")
    return _replace_at(events, i, make_chord(chord.root + 6, "7"))


def secondary_dominant(
    events: list[ChordEvent], i: int, key: Key, ts: TimeSignature
) -> list[ChordEvent]:
    """Insert V7 of the chord, taking half of the previous chord's time (or of its own)."""
    target = events[i]
    dominant = make_chord(target.chord.root + 7, "7")
    prev = (i - 1) % len(events)
    out = list(events)
    if len(events) > 1 and _beats(events[prev], ts) >= 2:
        keep, give = _split(events[prev], ts)
        out[prev] = _with_beats(events[prev], keep, ts)
        out.insert(prev + 1, ChordEvent(dominant, give))
    else:
        first, second = _split(target, ts)
        out[i : i + 1] = [ChordEvent(dominant, first), ChordEvent(target.chord, second)]
    return out


def chromatic_mediant(
    events: list[ChordEvent], i: int, key: Key, ts: TimeSignature
) -> list[ChordEvent]:
    """A chord a major third away with the same quality (C -> E, Am -> Fm): cinematic color."""
    chord = events[i].chord
    if _is_major(chord):
        return _replace_at(events, i, make_chord(chord.root + 4, ""))
    if _is_minor(chord):
        return _replace_at(events, i, make_chord(chord.root - 4, "m"))
    raise NotApplicable("only major and minor chords")


def sus_resolve(events: list[ChordEvent], i: int, key: Key, ts: TimeSignature) -> list[ChordEvent]:
    """Delay the chord's third: first half sus4, then the chord."""
    chord = events[i].chord
    if not (_is_major(chord) or _is_minor(chord)):
        raise NotApplicable("only major and minor chords")
    first, second = _split(events[i], ts)
    out = list(events)
    out[i : i + 1] = [ChordEvent(make_chord(chord.root, "sus4"), first), ChordEvent(chord, second)]
    return out


def passing_diminished(
    events: list[ChordEvent], i: int, key: Key, ts: TimeSignature
) -> list[ChordEvent]:
    """End the chord with a diminished seventh a semitone below the next chord's root."""
    if len(events) < 2:
        raise NotApplicable("needs a next chord")
    nxt = events[(i + 1) % len(events)].chord
    first, second = _split(events[i], ts)
    out = list(events)
    out[i : i + 1] = [
        ChordEvent(events[i].chord, first),
        ChordEvent(make_chord(nxt.root - 1, "dim7"), second),
    ]
    return out


def deceptive(events: list[ChordEvent], i: int, key: Key, ts: TimeSignature) -> list[ChordEvent]:
    """A tonic reached from the dominant becomes vi (major) or VI (minor)."""
    prev = events[(i - 1) % len(events)].chord
    chord = events[i].chord
    if chord.root != key.tonic or prev.root != (key.tonic + 7) % 12:
        raise NotApplicable("needs a dominant followed by the tonic")
    target = (
        make_chord(key.tonic + 9, "m") if key.mode is Mode.MAJOR else make_chord(key.tonic + 8, "")
    )
    return _replace_at(events, i, target)


# ---- progression operators ----------------------------------------------------------------


def sevenths(events: list[ChordEvent], i: int, key: Key, ts: TimeSignature) -> list[ChordEvent]:
    """Diatonic triads become their seventh chords (C -> Cmaj7, Dm -> Dm7, G -> G7)."""
    pairs = zip(diatonic_chords(key), diatonic_chords(key, sevenths=True), strict=True)
    triads = {triad.pitch_class_set: seventh for triad, seventh in pairs}
    out = [replace(e, chord=triads.get(e.chord.pitch_class_set, e.chord)) for e in events]
    if out == events:
        raise NotApplicable("no diatonic triads to enrich")
    return out


def tonic_pedal(events: list[ChordEvent], i: int, key: Key, ts: TimeSignature) -> list[ChordEvent]:
    """Every chord over the tonic in the bass (slash chords): tension over a fixed floor."""
    out = []
    for e in events:
        pcs = e.chord.pitch_class_set | {key.tonic}
        out.append(replace(e, chord=ChordSlot(e.chord.root, e.chord.quality, pcs)))
    if out == events:
        raise NotApplicable("every chord already contains the tonic")
    return out


def negative_harmony(
    events: list[ChordEvent], i: int, key: Key, ts: TimeSignature
) -> list[ChordEvent]:
    """Mirror every pitch class around the axis between the tonic and the dominant: in C,
    C -> Cm, G -> Fm, F -> Gm, Am -> Eb. The 'shadow' of the progression."""
    axis = 2 * key.tonic + 7
    out = []
    for e in events:
        mirrored = frozenset((axis - pc) % 12 for pc in e.chord.pitch_class_set)
        fifth = (e.chord.root + 7) % 12
        chord = identify_chord(mirrored, prefer_root=(axis - fifth) % 12)
        if chord is None:
            raise NotApplicable("a chord has no name in its mirrored form")
        out.append(replace(e, chord=chord))
    return out


def double_time(events: list[ChordEvent], i: int, key: Key, ts: TimeSignature) -> list[ChordEvent]:
    """Chords change twice as fast (the progression lasts half as long)."""
    if any(_beats(e, ts) < 2 or _beats(e, ts) % 2 for e in events):
        raise NotApplicable("some chords cannot be halved")
    return [_with_beats(e, _beats(e, ts) // 2, ts) for e in events]


def half_time(events: list[ChordEvent], i: int, key: Key, ts: TimeSignature) -> list[ChordEvent]:
    """Chords last twice as long (the progression lasts twice as long)."""
    if any(_beats(e, ts) * 2 > 64 for e in events):
        raise NotApplicable("chords would become too long")
    return [_with_beats(e, _beats(e, ts) * 2, ts) for e in events]


def step_up(events: list[ChordEvent], i: int, key: Key, ts: TimeSignature) -> list[ChordEvent]:
    """Everything a whole tone higher: the classic lift for a last chorus."""
    return [
        replace(
            e,
            chord=ChordSlot(
                (e.chord.root + 2) % 12,
                e.chord.quality,
                frozenset((pc + 2) % 12 for pc in e.chord.pitch_class_set),
            ),
        )
        for e in events
    ]


OPERATORS: dict[str, Operator] = {
    op.id: op
    for op in (
        Operator("relative", "chord", relative),
        Operator("borrow", "chord", borrow),
        Operator("tritone_sub", "chord", tritone_sub),
        Operator("secondary_dominant", "chord", secondary_dominant),
        Operator("chromatic_mediant", "chord", chromatic_mediant),
        Operator("sus_resolve", "chord", sus_resolve),
        Operator("passing_diminished", "chord", passing_diminished),
        Operator("deceptive", "chord", deceptive),
        Operator("sevenths", "progression", sevenths),
        Operator("tonic_pedal", "progression", tonic_pedal),
        Operator("negative_harmony", "progression", negative_harmony),
        Operator("double_time", "progression", double_time),
        Operator("half_time", "progression", half_time),
        Operator("step_up", "progression", step_up),
    )
}


def transform(
    operator_id: str,
    events: Sequence[ChordEvent],
    index: int,
    key: Key,
    ts: TimeSignature = FOUR_FOUR,
) -> list[ChordEvent]:
    if operator_id not in OPERATORS:
        raise KeyError(operator_id)
    if not events:
        raise NotApplicable("empty progression")
    if not 0 <= index < len(events):
        raise NotApplicable("no such chord")
    return OPERATORS[operator_id].apply(list(events), index, key, ts)
