"""Test doubles."""

from __future__ import annotations

import random
import threading
from typing import Any

from app.core.model import Note, Role
from app.core.timebase import STEP_TICKS, bars_to_ticks
from app.gen.adapter import GenerationSpec
from app.gen.engine import GenerationCancelled, ProgressFn, RawCandidate


class FakeEngine:
    """Deterministic engine: notes depend only on (seed, spec). Records every spec it gets."""

    def __init__(self, block: threading.Event | None = None) -> None:
        self.calls: list[GenerationSpec] = []
        self.block = block  # if set, sample() waits on it (to test queueing / cancellation)

    def info(self) -> dict[str, Any]:
        return {"model": "fake", "num_bars_map": [4, 8], "attribute_sizes": {}, "genres": []}

    def sample(
        self,
        spec: GenerationSpec,
        cancel: threading.Event | None = None,
        progress: ProgressFn | None = None,
    ) -> list[RawCandidate]:
        self.calls.append(spec)
        if progress:
            progress("sampling", {"model": "fake", "n_candidates": spec.n_candidates})
        if self.block is not None:
            while not self.block.wait(0.01):
                if cancel is not None and cancel.is_set():
                    raise GenerationCancelled()
        if cancel is not None and cancel.is_set():
            raise GenerationCancelled()
        return [
            RawCandidate(seed=spec.seed + i, notes=fake_notes(spec, spec.seed + i))
            for i in range(spec.n_candidates)
        ]


def fake_notes(spec: GenerationSpec, seed: int) -> tuple[Note, ...]:
    rng = random.Random(seed)
    total_steps = bars_to_ticks(spec.bars, spec.ts) // STEP_TICKS
    every = rng.choice([2, 4, 8])
    notes = []
    for step in range(0, total_steps, every):
        if spec.target_role is Role.DRUMS:
            pitch = 36 if step % 4 == 0 else rng.choice([38, 42])
        else:
            pitch = rng.randint(spec.target_spec.low - 5, spec.target_spec.high + 5)
        notes.append(Note(t=step * STEP_TICKS, p=pitch, d=every * STEP_TICKS, v=90))
    return tuple(notes)
