# midigpt notes (M1 spike)

Verified against the installed package **midigpt 0.4.2** (Windows wheel `cp310-win_amd64`, torch 2.14.1 CPU) by reading its source and by round-trip probes. Runtime model findings (attribute names/levels per checkpoint) are **pending**: see *Status*.

## Status

| Item | State |
|---|---|
| Package install (`.[inference]`) on Windows / Python 3.10 | OK |
| Python types (`Score`, `Track`, `Bar`, `Note`) | Verified (below) |
| Inference API (`InferenceEngine`, `GenerationRequest`, `TrackPrompt`, `InferenceConfig`) | Verified from source (below) |
| Score → `.mid` → Score round trip, tempo, PPQ, program | Verified with a probe |
| Load `yellow_medium` / `prism_medium` | **Blocked: HF repo is gated** |
| Per-model attributes, value labels, `num_bars_map`, genres | Pending (needs weights) |
| 4-bar bass on a 4-chord grid → `.mid` (M1 acceptance) | Pending (needs weights) |

### Gated weights

`InferenceEngine.from_pretrained(name)` downloads from `Metacreation/MIDI-GPT` on Hugging Face, which is **gated**. One-time setup:

1. Accept the licence at <https://huggingface.co/Metacreation/MIDI-GPT> with a Hugging Face account.
2. Authenticate: `.venv\Scripts\hf auth login` (or set `HF_TOKEN`).
3. Re-run `python scripts/m1_spike.py` (writes `output/m1/report.json` and `.mid` files) and complete this document.

Once cached, `from_pretrained` falls back to the local copy when the Hub is unreachable.

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

## Implications for M2

- `pitch_mask` with the bar's chord/scale pitch classes plus a `uniform` shape on the role range gives hard harmonic/range guidance even when the model has no chord attribute (relevant for `yellow_medium`). The post-processor and scorer remain the source of truth.
- `num_candidates` + `run_variations()` can implement the N-candidate loop in one call; SSE note streaming then only works for N=1, so stream progress (not notes) for N>1.
