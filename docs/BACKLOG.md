# Backlog

Single source of truth for what is done, what is next and what is undecided. Milestones and acceptance criteria are defined in `CLAUDE.md` §10; this file tracks their status and the concrete work items. Update it in the same commit that completes or changes an item.

Last review: 2026-11-26.

Legend: ✅ done · 🟡 in progress · ⬜ to do · ❓ needs a decision first.
Priority: **P1** next up · **P2** soon · **P3** later / nice to have.

## Milestone status

| # | Scope | Status | Notes |
|---|---|---|---|
| M0 | Repo, tooling, schema + Alembic, core model + timebase | ✅ | `make test` green; schema migrates from empty. |
| M1 | Model spike | ✅ | `scripts/m1_spike.py`, findings in `docs/midigpt-notes.md`. |
| M2 | Adapter, engine, candidates, scorer, post-processing, `/generate` + SSE | ✅ | 4 candidates, best by S, same seed ⇒ same notes, with the real model too. |
| M3 | Vanilla frontend: arrangement timeline, transport, playback, export | ✅ | Playback confirmed audible by the user (2026-11-26). Tone.js timbres judged poor → replaced by SpessaSynth + SoundFont banks (B-01…B-04). |
| C1 | Harmony: chord lane, diatonic chords, suggestions (rule-based planner) | ✅ | Chord lane + chord dialog checked in headless Chrome (2026-11-26). Order decided 2026-11-26: C1 → C2 → C3 → C4 → M4 → M5. |
| H | **Harmonic explorer** (progression picker: library + corpus + generator + prompt) | 🟡 | **Top priority (user, 2026-11-26)**, before finishing C2. Items B-55…B-59. |
| C2 | Harmony adherence + benchmark | 🟡 | Items B-20, B-70…B-74. |
| C3 | Prompt per part ("Regenerate with note") | ⬜ | Items B-16, B-80…B-84. |
| C4 | Song from prompt + "Generate all" | ⬜ | Items B-21, B-22, B-41, B-90…B-94. |
| M4 | Clip editor, replace / vary / lock / history, section reorder + repeat / duplicate | ⬜ | After C4. Items B-10…B-19. |
| M5 | Import `.mid`, benchmark | ⬜ | Items B-40, B-42 (planner moved to C1/C4). |
| M6 | Packaging (PyInstaller, pywebview, CI matrix) | ⬜ | Items B-50…B-51. |

## Open decisions

| ID | Question | Options | Blocks |
|---|---|---|---|
| D1 ✅ | Which JS SoundFont synth and which banks? | **Decided (2026-11-26):** SpessaSynth (Apache-2.0) + MuseScore General (MIT) as default bank, user import for any other bank. Criteria: maximum quality, import of downloaded banks, open source. `docs/audio-playback.md`. | — |
| D2 ✅ | What does "Duplicate section" do? | **Decided (2026-11-26):** two commands — "Repeat" (new instance of the same section, edits apply everywhere) and "Duplicate as new" (independent copy). | — |
| D3 ✅ | How should bass/harmony follow chord changes? | **Decided (2026-11-26):** all layers, CLAUDE.md §6.8 — `pitch_class_set` spike, deterministic harmonic snap, optional strict-harmony block generation, per-role CT weight + N=8 on yellow. | — |
| D4 ✅ | What is "Regenerate with note" (CLAUDE.md §8)? | **Decided (2026-11-26):** free-text prompt → structured `GenerationIntent` (CLAUDE.md §6.7), keyword interpreter offline, local Ollama when available. | — |
| D6 ✅ | Which LLM backend? | **Decided (2026-11-26):** local Ollama only, stdlib HTTP, rule-based fallback. | — |
| D7 ✅ | How should the progression picker work? | **Decided (2026-11-27):** all layers — harmonic rhythm (B-55), curated library with song kits + audition (B-56), optional local import of Chordonomicon (MIT) / ChoCo (mostly CC-BY) (B-57), generator + operators with an audacity control and surprise meter (B-58), prompt via Ollama mapped to parameters (B-59). | — |
| D5 ❓ | Should the master export include muted tracks? | Today: yes (mute = playback state only). Alternative: skip muted, or ask at export. | B-36 |

## H — Harmonic explorer (next up)

| ID | Item | Status |
|---|---|---|
| B-55 | Harmonic rhythm: chord events with `beats` (no migration: JSON field, no `beats` = one bar), text syntax `C*2 (Am F) G:3 %`, tick timeline for generator / snap / scorer, chord lane with proportional widths, event editor (duration, split, insert, delete) | ✅ |
| B-56 | Curated library (`core/library.py`: 45 progressions, 12 song kits, roman numerals + harmonic rhythm, tags kind / genre / mood / energy), planner on top of it, voice-led audition (`/harmony/audition.mid`), mood filters + ▶ in the chord dialog, "Kit armonici" dialog that fills or creates the song form. Audio checked offline only: **listen in a real browser pending** | ✅ |
| B-57 | Optional corpus import into `data/` (git-ignored, never bundled): Chordonomicon / ChoCo → roman numerals by section → n-gram statistics; search by pattern | ⬜ |
| B-58 | Generator + transformation operators (substitutions, borrowed chords, chromatic mediants, modulation for the last chorus, pedal, deceptive cadence) with "audacity" control and a surprise meter | ⬜ |
| B-59 | Prompt → harmonic parameters (Ollama, keyword fallback) → ranked candidates with an explanation | ⬜ |

## P1 — next up

| ID | Item | Status | Notes |
|---|---|---|---|
| B-01 | **SoundFont playback with SpessaSynth** (replaces Tone.js) | ✅ | Plays the server-exported MIDI via the SpessaSynth `Sequencer`; loop from export loop markers; live mute/solo on MIDI channels; Tone.js removed (`b7f76d7`). Verified headless by offline rendering with the real bank; **live listening check by the user pending** (B-05). |
| B-02 | Section-range MIDI export for playback | ✅ | `?start=&end=&loop=true` (`77a7066`). |
| B-03 | Sound bank storage and default bank | ✅ | `data/soundfonts/` (git-ignored), list / upload / serve / active / delete, `fetch-soundfont` and in-app download of MuseScore General (`f256fe4`). |
| B-04 | "Suoni" dialog: import, choose active, delete, licence notes | ✅ | (`b7f76d7`). |
| B-05 | Listen to the new playback in a real browser (section, loop, play all, mute/solo, bank switch) | 🟡 | Headless browsers cannot run the AudioWorklet. |
| B-06 | Optional: per-project bank, reverb/chorus amount, master volume | ⬜ | P3 ideas, not requested yet. |
| B-10 | Section commands in the timeline: rename, repeat / duplicate as new (D2), delete instance, insert a new section at a position | ⬜ | API exists: `PATCH /sections/{id}`, `PUT /projects/{id}/arrangement`, `DELETE /sections/{id}`. |
| B-11 | Drag section blocks to reorder | ⬜ | `PUT /projects/{id}/arrangement`. |
| B-12 | Lock / unlock a part in the UI | ⬜ | API exists (`PATCH /clips/{id}` `locked`). Locked parts are never regenerated and always used as context. |
| B-13 | **Vary**: `POST /generate/vary` + button | ⬜ | Next-best candidate from the last generation; candidates already kept in memory (`app.state.candidates`). |
| B-14 | **History**: versions list in the UI + `POST /clips/{id}/restore/{version_id}` | ⬜ | `GET /clips/{id}/versions` exists; restore endpoint missing. |

## P2 — soon

| ID | Item | Status | Notes |
|---|---|---|---|
| B-15 | **Replace**: set a part to another existing clip | ⬜ | Endpoint missing. |
| B-16 | Regenerate with note | ⬜ | → C3 (B-80…B-84). |
| B-17 | Clip editor: piano roll on canvas (pan/zoom, draw/move/resize/delete, snap to 16th) | ⬜ | Saves a `manual` version via `PATCH /clips/{id}` `notes`. 60 fps for 64 bars × 6 tracks. |
| B-18 | Drum step grid for drum tracks | ⬜ | `core/drums.py` has grid ↔ notes. |
| B-19 | M4 acceptance: full replace / move / assemble flow without reload | ⬜ | |
| B-20 | Bass and harmonic parts follow chord changes | ⬜ → C2 | Today CT ≈ 0.5 on Am–F–C–G; best bass is often a pedal on the tonic. |
| B-21 | Use **neighbouring sections** as context within the model window | ⬜ | CLAUDE.md §6.1; today only the other parts of the same section are context. |
| B-22 | Test and fix sections longer than the largest window (16 bars prism, 8 yellow) | ⬜ | Relies on the library's windowing; "2 bars overlap, earlier window wins" not verified with the real model. |
| B-30 | Delete projects, tracks and sections from the UI | ⬜ | API exists. |
| B-31 | Edit the time signature in the UI | ⬜ | API and export already support it. |

## P3 — later

| ID | Item | Status | Notes |
|---|---|---|---|
| B-23 | Triplet grid as a project setting | ⬜ | Supported by `core/postprocess.py`, not exposed. |
| B-24 | Humanize (timing/velocity jitter, seeded) as a generation option | ⬜ | `core/postprocess.humanize` exists, not wired. |
| B-25 | Stream the first candidate's notes over SSE | ⬜ | Optional in CLAUDE.md §7; midigpt's `note_sink` only works with one candidate. |
| B-26 | Say in the UI that "Vary" candidates are lost on server restart (in-memory store) | ⬜ | Or persist them if it turns out to matter. |
| B-32 | Dev mode with a fake engine, to work on the UI without loading the model | ⬜ | e.g. `ONYRIX_ENGINE=fake`. |
| B-36 | Muted tracks in the master export | ❓ D5 | |

## Composition roadmap (C1–C4)

| ID | Item | Status |
|---|---|---|
| B-60 | `core/harmony`: `chord_symbol` (inverse of `parse_chord`), `diatonic_chords`, `roman_numeral`, `suggest_next` (functional, secondary dominant, modal borrowing, tritone sub, relative) | ✅ |
| B-61 | `RuleBasedPlanner.suggest_progressions` per mode × genre × section kind, length variants, cadences | ✅ |
| B-62 | `/harmony/diatonic`, `/harmony/suggest`, `/harmony/next` | ✅ |
| B-63 | Chord lane in the timeline: per-section grid editing with server validation | ✅ |
| B-64 | Suggestion popovers: progression for the selected section, chord change on a bar | ✅ |
| B-70 | Spike: prism `pitch_class_set` = count of pitch classes per bar (set for chords/pad). Found and fixed: the target was generated by infill instead of autoregressively (monophonic chord parts, 2× slower). `docs/midigpt-notes.md` | ✅ |
| B-71 | `postprocess.harmonic_snap` (role-aware, idempotent, property-tested) | ✅ |
| B-72 | Strict harmony mode: block generation aligned to chord changes, per-block `pitch_mask` | ⬜ |
| B-73 | Per-role scorer weights ✅ (bass/chords/pad weigh CT more); N=8 default on `yellow_medium` ⬜ | 🟡 |
| B-74 | Benchmark CT / S / latency per role × mode (raw, snap, strict, strict+snap) | ⬜ |
| B-80 | `core/intent.GenerationIntent` + clamping | ⬜ |
| B-81 | `KeywordInterpreter` (it/en) and `OllamaInterpreter` (stdlib HTTP, JSON schema, fallback) | ⬜ |
| B-82 | Intent → midigpt controls via `ModelCaps` (durations, polyphony, silence, register, rhythm mask, remix) and scorer targets | ⬜ |
| B-83 | `/generate` `prompt`; prompt + resolved intent in version params; `/llm/status` | ⬜ |
| B-84 | UI "Regenerate with note" with quick chips, resolved intent shown | ⬜ |
| B-90 | `Plan` model, `RuleBasedPlanner.plan` and `LLMPlanner` (validated, repaired) | ⬜ |
| B-91 | `/projects/{id}/plan` preview + `/plan/apply` | ⬜ |
| B-92 | `/projects/{id}/generate-all`: one cancellable job, §6.1 order, per-cell SSE, skips locked / filled | ⬜ |
| B-93 | Section energy → intent; drum fill on the last bar; velocity by energy | ⬜ |
| B-94 | UI: "New song from prompt" dialog and "Generate all" | ⬜ |

## M5 — work items

| ID | Item | Status |
|---|---|---|
| B-40 | `POST /import/midi`: import a `.mid` as clips (context or content) | ⬜ |
| B-41 | `RuleBasedPlanner` / `LLMPlanner` | → C1 (B-61) and C4 (B-90) |
| B-42 | `scripts/benchmark_models.py` (stub today): mean S and latency per model over 20 runs; `make bench` | ⬜ |

## M6 — work items

| ID | Item | Status |
|---|---|---|
| B-50 | GitHub Actions matrix (ubuntu / macos / windows): lint + tests | ⬜ |
| B-51 | PyInstaller build per OS with a pywebview window; weights never bundled (licence) | ⬜ |

## Done (recent)

- ✅ SoundFont playback: SpessaSynth + MuseScore General, bank import/management, section-range export (B-01…B-04).

- ✅ M3 accepted: playback audible in the browser (user check, 2026-11-26).
- ✅ Timeline arrangement view: tracks as rows, time left → right, sections as bar blocks, zoom, playhead (`5c3dad5`).
- ✅ Vanilla web UI, Tone.js vendored, `.mid` export (`5ec6d71`, `e683d31`, `75b8baf`).
- ✅ Track-level `pitch_mask` fix (per-bar masks were ignored by midigpt) with regression tests (`2453a5c`).
