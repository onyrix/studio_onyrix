# midigpt notes (M1 spike)

Verified against the installed package **midigpt 0.4.2** (Windows wheel `cp310-win_amd64`, torch 2.14.1 CPU) by reading its source, by round-trip probes, and by running `scripts/m1_spike.py` on both checkpoints (CPU, seed 1234).

## Status — M1 acceptance met

| Item | State |
|---|---|
| Package install (`.[inference]`) on Windows / Python 3.10 | OK |
| Python types and inference API | Verified (below) |
| Load `yellow_medium` / `prism_medium` | OK (≈30 s first load incl. download, ≈3 s cached) |
| Per-model attributes, windows, genres | Recorded (below) |
| 4-bar bass on Am–F–C–G, 4 candidates → valid `.mid` (PPQ 480, tempo, GM programs) | OK for both models |
| Same seed ⇒ same notes | OK for both models |
| `make test-infer` | 4 passed |

### Gated weights

`Metacreation/MIDI-GPT` on Hugging Face is **gated**. One-time setup: accept the licence at <https://huggingface.co/Metacreation/MIDI-GPT>, then `hf auth login` (or set `HF_TOKEN`). Once cached, `from_pretrained` falls back to the local copy when the Hub is unreachable.

## Runtime model facts

| | `yellow_medium` | `prism_medium` |
|---|---|---|
| Windows (`num_bars_map`) | 4, 8 | 4, 8, 12, 16 |
| Max context tokens | 2048 | 4096 |
| Internal resolution | 12 ticks/quarter | 12 ticks/quarter |
| Genres (`request.controls["genre"]`) | none | 18: asian, baroque, blues, christian, classical, country, dance-electronic, european, folk, hip-hop, jazz, latin, metal, pop, punk, renaissance, rock, soundtrack |
| Switchable velocity / microtiming | no / no | no / no |
| Generate 4 bars × 4 candidates (CPU) | ≈24 s | ≈8.5 s |

Attributes (`attribute_sizes`, `attribute_levels`, `attribute_track_types`):

| Model | Attribute | Levels | Scope | Tracks | Labels |
|---|---|---|---|---|---|
| yellow | `note_density` | 10 | track | drum | `sparsest (Q0)` … `densest (Q9)` |
| yellow | `min_polyphony`, `max_polyphony` | 10 | track | melodic | `1 voice` … `10+ voices` |
| yellow | `min_note_duration`, `max_note_duration` | 6 | track | melodic | `32nd` … `whole` |
| prism | `key_signature` | 25 | track | melodic | (no labels) |
| prism | `pitch_range` | 128 | track | melodic | (no labels) |
| prism | `silence_proportion` | 10 | track | both | (no labels) |
| prism | `min_note_duration`, `max_note_duration` | 6 | track | melodic | `32nd` … `whole` |
| prism | `bar_note_density` | 10 | bar | drum | `sparsest (Q0)` … `densest (Q9)` |
| prism | `bar_min_polyphony`, `bar_max_polyphony` | 10 | bar | melodic | `1 voice` … `10+ voices` |
| prism | `pitch_class_set` | 13 | bar | melodic | (no labels) |

Note: density is a **drum-only** attribute on both checkpoints; for melodic roles density can only be steered indirectly (polyphony, note duration, silence proportion) or via `rhythm_mask`.

### Raw output quality (why post-processing and scoring are mandatory)

Bass, 4 candidates each, before any post-processing (role range 28–55, 16th grid, chord tones on quarter-note onsets):

| Model | Seed | Notes | In range | On 16th grid | Chord tones on beats |
|---|---|---|---|---|---|
| yellow | 1234 | 8 | 8/8 | 8/8 | 1/4 |
| yellow | 1235 | 84 | 28/84 | 44/84 | 5/12 |
| yellow | 1236 | 8 | 8/8 | 8/8 | 2/8 |
| yellow | 1237 | 64 | 48/64 | 64/64 | 16/16 |
| prism | 1234 | 8 | 8/8 | 8/8 | 2/4 |
| prism | 1235 | 4 | 0/4 | 4/4 | 2/4 |
| prism | 1236 | 16 | 16/16 | 16/16 | 4/8 |
| prism | 1237 | 4 | 4/4 | 4/4 | 2/4 |

Candidates vary wildly (4 to 84 notes, out-of-range and off-grid notes, very short durations of 40–80 ticks). This confirms CLAUDE.md rule 8: never use raw output; generate N candidates, post-process, score, keep the best. Harmonic guidance (`pitch_mask` / `pitch_class_set`) was **not** used in this spike.

## Types (`midigpt._types`, plain dataclasses)

```python
Note(pitch, velocity, onset_ticks, duration_ticks, delta=0)  # onset is RELATIVE TO ITS BAR
Bar(notes=[], ts_numerator=4, ts_denominator=4, beat_length=4.0, future=False)
Track(bars=[], instrument=0, track_type="melodic" | "drum", attributes={})
Score(tracks=[], resolution=480, tempo=500000)  # tempo in µs per quarter
Score.from_midi(path) / from_bytes(data) / to_midi(path) / resample(tpq) / to_dict() / from_dict()
```

- Probe: bar 1 note with `onset_ticks=480` is written at absolute tick 2400 (= 1920 + 480). **Adapter must convert clip-relative ticks to (bar index, bar-relative onset).**
- `to_midi` writes PPQ 480, `set_tempo`, `time_signature`, one `program_change` per track. Track names are not written; our own `midi_io.py` (mido) stays responsible for the export format.
- Decoded scores carry the default tempo; `SamplingSession` restores the input tempo.

## Inference API (`midigpt.inference`)

- `InferenceEngine.from_pretrained(name, hf_repo="Metacreation/MIDI-GPT", device=None, token=None)`; also `from_checkpoint(path)`. Calls `warmup()` itself.
- `engine.session(score, request) -> SamplingSession` (validates the request against the encoder config and analyzer).
- `SamplingSession.run() -> Score`; `run_variations() -> [{"score", "seed", "gen_count", "error"}]` for `config.num_candidates > 1`, seeds `base, base+1, ...`, batched into one decode when the plan is a single step without hidden spans.
- `session.resolved_seed`: the actual seed used (random if `config.seed < 0`). Store it with the ClipVersion.
- Cancellation: set `session.cancel_event = threading.Event()` before `run()`; set it to abort → `GenerationCancelled(partial, gen_count)`.
- Streaming: `session.note_sink(list[dict])` gets completed notes `{track, bar, pitch, onset_ticks, duration_ticks, velocity}` — **single-candidate path only** (not with `num_candidates > 1`).
- `TrackPrompt(id, bars, autoregressive=False, ignore=False, mask_bars=[], attributes={}, controls={}, bar_attributes={}, bar_controls={})` — names match CLAUDE.md 6.2.
- `controls` supports `pitch_mask` (`{"pitch_classes": [...]}`, `{"scale": "...", "root": n}`, optional `shape` uniform/normal for register), `rhythm_mask` (`grid` soft quantize, or exact `positions`), `remix` (`{"amount", "mode"}` — variation of existing content), `time_signature`.
- `GenerationRequest.controls`: piece-level `genre` (string from the checkpoint's genre groups), `velocity`, `microtiming`.
- `InferenceConfig` defaults: `temperature=1.0`, `top_p=1.0`, `mask_mode="auto"`, `model_dim=4`, `max_attempts=3`, `novelty_check=True`, `silence_check=True`. Our defaults per CLAUDE.md: `mask_mode="attention"`, `top_p=0.95`. `model_dim`, `bars_per_step`, `tracks_per_step` accept `"auto"`.
- Long sections: the library's planner already windows (`model_dim`, `bars_per_step`, `ar_overlap`, `min_overlap_bars=2`) and may drop context tracks to fit (`context="auto"`; `context_keep` protects tracks — use it for locked clips).
- Runtime introspection (same as the HTTP `/info` handler): `engine._analyzer.attribute_sizes()`, `.attribute_value_labels()`, `.attribute_levels()`, `.attribute_track_types()`; `json.loads(engine._tokenizer._vocab.config().to_json())["num_bars_map"]`; `engine._model.max_context()`.
- Attribute registry names (which ones a checkpoint uses is pending): `note_density`, `onset_polyphony`, `pitch_range`, `key_signature`, `note_duration_dist`, `silence_proportion`, `pitch_class_set`, `note_density_quantile`, `polyphony_quantile`, `note_duration_quantile`, `tension`, `tension_drum`, `nomml`.

## M2 findings

- **`bar_controls` only honours `time_signature`.** A `pitch_mask` inside `bar_controls` passes `validate_request` but is silently ignored by `SamplingSession` (it reads only `time_signature` there). `pitch_mask` works **only** in track-level `TrackPrompt.controls`, one mask per step. Per-bar *attributes* (`bar_attributes`, e.g. `bar_max_polyphony`) are honoured. The adapter therefore sends one track-level mask: key scale (or union of chord tones when there is no key) + role range as a `uniform` shape. Regression tests: `tests/gen/test_adapter.py::test_pitch_mask_is_track_level_not_bar_level`, `tests/inference/test_pipeline.py::test_raw_output_respects_pitch_mask`.
- **Chord following is weak.** With the mask applied, raw bass stays in scale and in range on both models, but on Am–F–C–G the best candidates are pedal tones on A (prism) or busy single-note lines (yellow): CT ≈ 0.5. Candidates for improvement later: more candidates (N=8), stronger chord context, generating bar by bar with per-bar masks (costs latency), or a higher CT weight for bass. Not addressed in M2.

## C2 findings (B-70, 2026-11-26)

- **`pitch_class_set` (prism, bar level, 13 levels) is a COUNT**, not a set: `len({pitch % 12})` of the bar's notes, quantized to 0–12 (`midigpt/attributes/pitch_class_set.py`). It cannot carry chord identity. The adapter sets it per bar for chords/pad to the size of that bar's chord; on its own it did not change the output measurably.
- **The target track must be generated with `autoregressive=True`.** The adapter used infill (`autoregressive=False`) on the always-empty target track. Prism then produced one repeated pitch class per bar for chords and pad (raw: 1 pitch class, 1 voice in every bar, every candidate, with or without `pitch_mask`, attributes or `bar_min_polyphony`). With `autoregressive=True`: 3–5 pitch classes per bar, up to 4–6 voices. Regression test: `tests/gen/test_adapter.py::test_target_track_is_generated_from_scratch`.
- Bass on Am–F–C–G, A minor, 6 requests × 4 candidates, CT measured on post-processed notes **before** the harmonic snap:

  | Model | Mode | Mean CT (all) | Mean CT (best) | Latency / request (CPU) |
  |---|---|---|---|---|
  | prism | infill | 0.48 | 0.54 | 15.9 s |
  | prism | autoregressive | 0.47 | **0.70** | **8.2 s** |
  | yellow | infill | 0.44 | 0.60 | 27.1 s |
  | yellow | autoregressive | 0.41 | 0.54 | **10.8 s** |

  After `harmonic_snap` (level `normal`) every beat of the kept bass is a chord tone by construction; the scorer still ranks on the pre-snap notes.

## Implications for M2

- **Resolution:** decoded scores come back at **resolution 1920**, whatever the input resolution was. The adapter must call `score.resample(480)` on every result before converting to clip notes (`scripts/m1_spike.py` does this).
- **Bar-relative onsets:** convert clip-relative ticks ↔ (bar index, onset within bar) in `adapter.py` via `core/timebase.py`.
- **Model differences:** `prism_medium` supports key, pitch range, bar-level pitch class set and genre; `yellow_medium` only polyphony, note duration and drum density. Build controls from `attribute_sizes()` at runtime, never hard-coded.

- `pitch_mask` (track-level, see *M2 findings*) with the scale's pitch classes plus a `uniform` shape on the role range gives hard key/range guidance even when the model has no key attribute (relevant for `yellow_medium`). The post-processor and scorer remain the source of truth.
- `num_candidates` + `run_variations()` can implement the N-candidate loop in one call; SSE note streaming then only works for N=1, so stream progress (not notes) for N>1.
