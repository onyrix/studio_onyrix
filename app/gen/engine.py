"""Model engines and the candidate loop (CLAUDE.md section 6.3).

`Engine` is the only interface the rest of the app sees. `MidiGptEngine` loads the model lazily
on first use (never at import time) and falls back to the secondary model if the primary fails.
The candidate loop post-processes, filters and scores every raw candidate: the model proposes,
`postprocess` and `scorer` decide.
"""

from __future__ import annotations

import json
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from app.core import drums
from app.core.model import Note, Role
from app.core.postprocess import harmonic_snap, postprocess
from app.core.scorer import (
    ScoreBreakdown,
    ScoringContext,
    hard_constraint_violation,
    score_notes,
)
from app.core.timebase import bars_to_ticks
from app.gen.adapter import GenerationSpec, ModelCaps, build_request, build_score, extract_notes

log = logging.getLogger(__name__)

ProgressFn = Callable[[str, dict[str, Any]], None]


class GenerationCancelled(Exception):
    pass


@dataclass(frozen=True)
class RawCandidate:
    seed: int
    notes: tuple[Note, ...]
    error: str | None = None


@dataclass(frozen=True)
class ScoredCandidate:
    seed: int
    notes: tuple[Note, ...]
    breakdown: ScoreBreakdown | None
    rejected: str | None = None

    @property
    def score(self) -> float:
        return self.breakdown.total if self.breakdown else -1.0


class Engine(Protocol):
    def info(self) -> dict[str, Any]: ...

    def sample(
        self,
        spec: GenerationSpec,
        cancel: threading.Event | None = None,
        progress: ProgressFn | None = None,
    ) -> list[RawCandidate]: ...


class MidiGptEngine:
    """In-process midigpt engine. Thread-safe; meant to be driven by a single worker."""

    def __init__(self, model_name: str, fallback_name: str | None = None, device: str = "auto"):
        self._names = [model_name] + ([fallback_name] if fallback_name else [])
        self._device = device
        self._lock = threading.Lock()
        self._engine: Any = None
        self._caps: ModelCaps | None = None

    @staticmethod
    def _resolve_device(device: str) -> str:
        if device != "auto":
            return device
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _load(self) -> tuple[Any, ModelCaps]:
        with self._lock:
            if self._engine is not None and self._caps is not None:
                return self._engine, self._caps
            from midigpt.inference import InferenceEngine

            device = self._resolve_device(self._device)
            errors = []
            for name in self._names:
                try:
                    engine = InferenceEngine.from_pretrained(name, device=device)
                except Exception as exc:
                    log.warning("could not load %s: %s", name, exc)
                    errors.append(f"{name}: {type(exc).__name__}: {exc}")
                    continue
                self._engine, self._caps = engine, self._read_caps(name, engine)
                log.info("loaded model %s on %s", name, device)
                return self._engine, self._caps
            raise RuntimeError("no model could be loaded: " + "; ".join(errors))

    @staticmethod
    def _read_caps(name: str, engine: Any) -> ModelCaps:
        analyzer = engine._analyzer
        enc = json.loads(engine._tokenizer._vocab.config().to_json())
        grouping = getattr(engine._tokenizer._vocab.config(), "genre_grouping", None)
        genres = (
            tuple(grouping.decode(i) for i in range(grouping.num_genres()))
            if grouping is not None
            else ()
        )
        return ModelCaps(
            name=name,
            num_bars_map=tuple(sorted(enc.get("num_bars_map") or [4])),
            attribute_sizes=dict(analyzer.attribute_sizes()),
            attribute_levels=dict(analyzer.attribute_levels()),
            attribute_track_types=dict(analyzer.attribute_track_types()),
            genres=genres,
            max_context_tokens=int(engine._model.max_context()),
        )

    def info(self) -> dict[str, Any]:
        _, caps = self._load()
        return caps.as_dict()

    def sample(
        self,
        spec: GenerationSpec,
        cancel: threading.Event | None = None,
        progress: ProgressFn | None = None,
    ) -> list[RawCandidate]:
        from midigpt.inference import GenerationCancelled as MidiGptCancelled

        engine, caps = self._load()
        if progress:
            progress("sampling", {"model": caps.name, "n_candidates": spec.n_candidates})
        score, target = build_score(spec)
        request = build_request(spec, target, caps)
        session = engine.session(score, request)
        session.cancel_event = cancel
        try:
            if spec.n_candidates > 1:
                results = session.run_variations()
            else:
                results = [{"score": session.run(), "seed": session.resolved_seed, "error": None}]
        except MidiGptCancelled:
            raise GenerationCancelled() from None
        out = []
        for r in results:
            if r["score"] is None:
                out.append(RawCandidate(seed=int(r["seed"]), notes=(), error=r.get("error")))
            else:
                notes = extract_notes(r["score"], target, spec.ts)
                out.append(RawCandidate(seed=int(r["seed"]), notes=notes))
        return out


def scoring_context(spec: GenerationSpec) -> ScoringContext:
    kicks: frozenset[int] = frozenset()
    for track in spec.context:
        if track.role is Role.DRUMS:
            kicks |= drums.onsets(track.notes, drums.KICKS)
    return ScoringContext(
        spec=spec.target_spec,
        bars=spec.bars,
        chords=spec.chords,
        kick_onsets=kicks or None,
        four_on_floor=drums.is_four_on_floor(spec.genre),
        ts=spec.ts,
    )


def finalize(notes: tuple[Note, ...], spec: GenerationSpec) -> tuple[Note, ...]:
    """Harmonic snap (CLAUDE.md 6.8) on post-processed notes, then post-process again to drop
    the duplicates a move may create."""
    clip_ticks = bars_to_ticks(spec.bars, spec.ts)
    snapped = harmonic_snap(
        notes, spec.chords, spec.target_spec, clip_ticks, spec.ts, level=spec.harmony
    )
    return postprocess(snapped, spec.target_spec, clip_ticks)


def rank_candidates(spec: GenerationSpec, raw: list[RawCandidate]) -> list[ScoredCandidate]:
    """Post-process, score, snap to the harmony and filter; best first, rejected last.

    The score is computed before the harmonic snap so it still ranks how well the model itself
    followed the chords; the kept notes are the snapped ones.
    """
    clip_ticks = bars_to_ticks(spec.bars, spec.ts)
    ctx = scoring_context(spec)
    scored = []
    for candidate in raw:
        if candidate.error:
            scored.append(ScoredCandidate(candidate.seed, (), None, f"error: {candidate.error}"))
            continue
        clean = postprocess(candidate.notes, spec.target_spec, clip_ticks)
        notes = finalize(clean, spec)
        violation = hard_constraint_violation(notes, ctx)
        if violation:
            scored.append(ScoredCandidate(candidate.seed, notes, None, violation))
        else:
            scored.append(ScoredCandidate(candidate.seed, notes, score_notes(clean, ctx)))
    # Higher score first; ties broken by seed so the order is reproducible.
    return sorted(scored, key=lambda c: (c.rejected is not None, -c.score, c.seed))


def generate_candidates(
    engine: Engine,
    spec: GenerationSpec,
    cancel: threading.Event | None = None,
    progress: ProgressFn | None = None,
) -> list[ScoredCandidate]:
    raw = engine.sample(spec, cancel, progress)
    if cancel is not None and cancel.is_set():
        raise GenerationCancelled()
    ranked = rank_candidates(spec, raw)
    if progress:
        for c in ranked:
            progress(
                "candidate",
                {"seed": c.seed, "score": round(c.score, 4), "rejected": c.rejected},
            )
    return ranked
