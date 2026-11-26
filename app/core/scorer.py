"""Candidate scoring (CLAUDE.md section 6.3). Pure.

S = w_ct*CT + w_r*R + w_d*(1 - min(1, |D - D*| / D*)) + w_o*(1 - O) + w_k*K
Drums replace CT with pattern coverage (same weight). All weights live here.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.core import drums
from app.core.model import Note, Role
from app.core.roles import RoleSpec
from app.core.timebase import FOUR_FOUR, PPQ, TimeSignature, bar_ticks

DEFAULT_WEIGHTS: dict[str, float] = {"ct": 0.4, "r": 0.2, "d": 0.2, "o": 0.1, "k": 0.1}
# Harmonic roles weigh chord tones more (D3, CLAUDE.md 6.8); K only means something for bass.
_HARMONIC: dict[str, float] = {"ct": 0.5, "r": 0.2, "d": 0.15, "o": 0.15, "k": 0.0}
ROLE_WEIGHTS: dict[Role, dict[str, float]] = {
    **{role: DEFAULT_WEIGHTS for role in Role},
    Role.BASS: {"ct": 0.45, "r": 0.15, "d": 0.15, "o": 0.1, "k": 0.15},
    Role.CHORDS: _HARMONIC,
    Role.PAD: _HARMONIC,
}


@dataclass(frozen=True)
class ScoringContext:
    spec: RoleSpec
    bars: int
    chord_pcs: Sequence[frozenset[int] | None] = ()  # per bar; None = no harmony for that bar
    kick_onsets: frozenset[int] | None = None  # clip-relative ticks of kick hits in context
    target_notes_per_bar: float | None = None  # overrides spec.target_notes_per_bar
    four_on_floor: bool = False
    ts: TimeSignature = FOUR_FOUR


@dataclass(frozen=True)
class ScoreBreakdown:
    total: float
    ct: float
    r: float
    d: float
    o: float
    k: float

    def as_dict(self) -> dict[str, float]:
        return {k: round(v, 4) for k, v in self.__dict__.items()}


def _beat_ticks(ts: TimeSignature) -> int:
    return PPQ * 4 // ts.denominator


def _strong_beat_notes(notes: Sequence[Note], ts: TimeSignature) -> list[Note]:
    beat = _beat_ticks(ts)
    return [n for n in notes if (n.t % bar_ticks(ts)) % beat == 0]


def chord_tone_ratio(notes: Sequence[Note], ctx: ScoringContext) -> float:
    if not any(ctx.chord_pcs):
        return 1.0  # no harmony to follow
    counted = 0
    hits = 0
    for note in _strong_beat_notes(notes, ctx.ts):
        bar = note.t // bar_ticks(ctx.ts)
        pcs = ctx.chord_pcs[bar % len(ctx.chord_pcs)]
        if pcs is None:
            continue
        counted += 1
        hits += note.p % 12 in pcs
    return hits / counted if counted else 0.0


def range_ratio(notes: Sequence[Note], spec: RoleSpec) -> float:
    if not notes:
        return 0.0
    return sum(spec.low <= n.p <= spec.high for n in notes) / len(notes)


def density_term(notes: Sequence[Note], bars: int, target: float) -> float:
    measured = len(notes) / bars
    return 1.0 - min(1.0, abs(measured - target) / target)


def overlap_ratio(notes: Sequence[Note], monophonic: bool) -> float:
    if not notes:
        return 0.0
    ordered = sorted(notes, key=lambda n: (n.t, n.p))
    bad: set[int] = set()
    for i, a in enumerate(ordered):
        for j in range(i + 1, len(ordered)):
            b = ordered[j]
            if b.t >= a.end:
                break
            if monophonic or a.p == b.p:
                bad.update((i, j))
    return len(bad) / len(ordered)


def kick_alignment(notes: Sequence[Note], ctx: ScoringContext) -> float:
    if ctx.spec.role is not Role.BASS or not ctx.kick_onsets:
        return 1.0
    strong = _strong_beat_notes(notes, ctx.ts)
    if not strong:
        return 0.0
    return sum(n.t in ctx.kick_onsets for n in strong) / len(strong)


def hard_constraint_violation(notes: Sequence[Note], ctx: ScoringContext) -> str | None:
    """Reason a candidate must be discarded before scoring, or None."""
    if not notes:
        return "empty"
    if (
        ctx.spec.is_drum
        and ctx.four_on_floor
        and drums.missing_downbeat_kick(notes, ctx.bars, ctx.ts)
    ):
        return "missing downbeat kick"
    return None


def score_notes(notes: Sequence[Note], ctx: ScoringContext) -> ScoreBreakdown:
    weights = ROLE_WEIGHTS[ctx.spec.role]
    target = ctx.target_notes_per_bar or ctx.spec.target_notes_per_bar
    if ctx.spec.is_drum:
        ct = drums.pattern_coverage(notes, ctx.bars, ctx.four_on_floor, ctx.ts)
    else:
        ct = chord_tone_ratio(notes, ctx)
    r = range_ratio(notes, ctx.spec)
    d = density_term(notes, ctx.bars, target)
    o = overlap_ratio(notes, ctx.spec.monophonic)
    k = kick_alignment(notes, ctx)
    total = (
        weights["ct"] * ct
        + weights["r"] * r
        + weights["d"] * d
        + weights["o"] * (1.0 - o)
        + weights["k"] * k
    )
    return ScoreBreakdown(total=total, ct=ct, r=r, d=d, o=o, k=k)
