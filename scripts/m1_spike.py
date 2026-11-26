"""M1 model spike (CLAUDE.md section 10).

Loads each midigpt checkpoint, dumps what it reports at runtime (attributes, value labels,
window sizes, capabilities), then generates 4 bars of bass on a 4-chord grid with a block-chord
piano track as context, and writes the result as a .mid file.

Downloads weights to the Hugging Face cache on first run. Not imported by the app or by tests.

Usage: python scripts/m1_spike.py [--models yellow_medium prism_medium] [--seed 1234]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import mido

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.timebase import PPQ, STEP_TICKS, bar_ticks, bpm_to_us_per_quarter  # noqa: E402

OUT_DIR = ROOT / "output" / "m1"
BPM = 100.0
# Am - F - C - G, one chord per bar: (name, MIDI pitches of a close voicing around C4)
CHORD_GRID = [
    ("Am", [57, 60, 64]),
    ("F", [53, 57, 60]),
    ("C", [55, 60, 64]),
    ("G", [55, 59, 62]),
]
BASS_RANGE = (28, 55)


def pick_device() -> str:
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def build_score(midigpt: Any) -> Any:
    """Track 0: piano block chords (context). Track 1: empty bass (to generate)."""
    from midigpt import Bar, Note, Score, Track

    chord_bars = []
    for _, pitches in CHORD_GRID:
        notes = [
            Note(pitch=p, velocity=80, onset_ticks=on, duration_ticks=2 * PPQ - 20)
            for on in (0, 2 * PPQ)
            for p in pitches
        ]
        chord_bars.append(Bar(notes=notes, ts_numerator=4, ts_denominator=4))
    piano = Track(bars=chord_bars, instrument=0, track_type="melodic")
    bass = Track(bars=[Bar() for _ in CHORD_GRID], instrument=33, track_type="melodic")
    return Score(tracks=[piano, bass], resolution=PPQ, tempo=bpm_to_us_per_quarter(BPM))


def describe(engine: Any) -> dict[str, Any]:
    analyzer = engine._analyzer
    enc = json.loads(engine._tokenizer._vocab.config().to_json())
    return {
        "resolution": engine._tokenizer._vocab.config().resolution,
        "num_bars_map": enc.get("num_bars_map"),
        "max_context_tokens": engine._model.max_context(),
        "attribute_sizes": analyzer.attribute_sizes(),
        "attribute_levels": analyzer.attribute_levels(),
        "attribute_track_types": analyzer.attribute_track_types(),
        "attribute_value_labels": analyzer.attribute_value_labels(),
        "switchable_velocity": enc.get("switchable_velocity"),
        "switchable_microtiming": enc.get("switchable_microtiming"),
        "genres": genres(engine),
        "token_domain_types": sorted({d.get("type") for d in enc.get("token_domains", [])}),
    }


def genres(engine: Any) -> list[str]:
    g = getattr(engine._tokenizer._vocab.config(), "genre_grouping", None)
    return [g.decode(i) for i in range(g.num_genres())] if g is not None else []


def generate_bass(engine: Any, score: Any, seed: int) -> tuple[Any, list[dict[str, Any]], float]:
    from midigpt.inference import GenerationRequest, InferenceConfig, TrackPrompt

    cfg = InferenceConfig(
        seed=seed, temperature=1.0, top_p=0.95, mask_mode="attention", model_dim=4, num_candidates=4
    )
    request = GenerationRequest(
        tracks=[
            TrackPrompt(id=0, bars=[]),  # context
            TrackPrompt(id=1, bars=[0, 1, 2, 3]),  # infill all 4 bars
        ],
        config=cfg,
    )
    started = time.perf_counter()
    candidates = engine.session(score, request).run_variations()
    elapsed = time.perf_counter() - started
    # Decoded scores come back at the tokenizer's output resolution (not the input's): resample.
    for c in candidates:
        if c["score"] is not None:
            c["raw_resolution"] = c["score"].resolution
            c["score"] = c["score"].resample(PPQ)
    best = next(c["score"] for c in candidates if c["score"] is not None)
    return best, candidates, elapsed


def bass_notes(score: Any) -> list[dict[str, int]]:
    """Flatten track 1 to clip-relative {t, p, d, v} (onsets are relative to their bar)."""
    assert score.resolution == PPQ, f"expected PPQ {PPQ}, got {score.resolution}"
    out = []
    bar_len = bar_ticks()
    for i, bar in enumerate(score.tracks[1].bars):
        for n in bar.notes:
            out.append(
                {
                    "t": i * bar_len + n.onset_ticks,
                    "p": n.pitch,
                    "d": n.duration_ticks,
                    "v": n.velocity,
                }
            )
    return sorted(out, key=lambda n: (n["t"], n["p"]))


def check_bass(notes: list[dict[str, int]]) -> dict[str, Any]:
    in_range = sum(BASS_RANGE[0] <= n["p"] <= BASS_RANGE[1] for n in notes)
    on_grid = sum(n["t"] % STEP_TICKS == 0 for n in notes)
    chord_tone_downbeats = 0
    downbeats = 0
    for n in notes:
        bar, pos = divmod(n["t"], bar_ticks())
        if pos % PPQ == 0 and bar < len(CHORD_GRID):
            downbeats += 1
            pcs = {p % 12 for p in CHORD_GRID[bar][1]}
            chord_tone_downbeats += n["p"] % 12 in pcs
    return {
        "notes": len(notes),
        "in_role_range": f"{in_range}/{len(notes)}",
        "on_16th_grid": f"{on_grid}/{len(notes)}",
        "chord_tones_on_beats": f"{chord_tone_downbeats}/{downbeats}",
    }


def write_mid(score: Any, path: Path) -> dict[str, Any]:
    score.to_midi(str(path))
    mid = mido.MidiFile(str(path))
    tempos = [m.tempo for t in mid.tracks for m in t if m.type == "set_tempo"]
    programs = [m.program for t in mid.tracks for m in t if m.type == "program_change"]
    return {
        "ticks_per_beat": mid.ticks_per_beat,
        "tempos": tempos,
        "programs": programs,
        "tracks": len(mid.tracks),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["yellow_medium", "prism_medium"])
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args()

    import midigpt
    from midigpt.inference import InferenceEngine

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    device = pick_device()
    print(f"midigpt {midigpt.__version__}, device={device}")
    report: dict[str, Any] = {"midigpt": midigpt.__version__, "device": device, "models": {}}

    for name in args.models:
        print(f"\n=== {name} ===")
        entry: dict[str, Any] = {}
        report["models"][name] = entry
        try:
            t0 = time.perf_counter()
            engine = InferenceEngine.from_pretrained(name, device=device)
            entry["load_seconds"] = round(time.perf_counter() - t0, 1)
        except Exception as exc:  # report and continue with the next model
            entry["load_error"] = f"{type(exc).__name__}: {exc}"
            print(entry["load_error"])
            continue
        entry["info"] = describe(engine)
        print(json.dumps(entry["info"], indent=2)[:4000])

        score = build_score(midigpt)
        best, candidates, elapsed = generate_bass(engine, score, args.seed)
        entry["generate_seconds_4_candidates"] = round(elapsed, 1)
        entry["candidates"] = [
            {
                "seed": c["seed"],
                "error": c["error"],
                "raw_resolution": c.get("raw_resolution"),
                "check": check_bass(bass_notes(c["score"])) if c["score"] is not None else None,
            }
            for c in candidates
        ]
        notes = bass_notes(best)
        entry["first_candidate_notes"] = notes
        # Reproducibility: same seed, single candidate, twice.
        again, _, _ = generate_bass(engine, score, args.seed)
        entry["reproducible_same_seed"] = bass_notes(again) == notes
        mid_path = OUT_DIR / f"bass_{name}_seed{args.seed}.mid"
        entry["midi"] = {"path": str(mid_path.relative_to(ROOT)), **write_mid(best, mid_path)}
        print(json.dumps({k: v for k, v in entry.items() if k != "info"}, indent=2))

    (OUT_DIR / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport written to {(OUT_DIR / 'report.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
