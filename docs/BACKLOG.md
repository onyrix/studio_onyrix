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
| M3 | Vanilla frontend: arrangement timeline, transport, playback, export | ✅ | Playback confirmed audible in the browser by the user (2026-11-26). Sound quality of Tone.js built-in synths judged poor → B-01. |
| M4 | Clip editor, replace / vary / lock / history, section reorder + duplicate | ⬜ | Next milestone. Items B-10…B-19. |
| M5 | Import `.mid`, rule-based planner, benchmark | ⬜ | Items B-40…B-42. |
| M6 | Packaging (PyInstaller, pywebview, CI matrix) | ⬜ | Items B-50…B-51. |

## Open decisions

| ID | Question | Options | Blocks |
|---|---|---|---|
| D1 ❓ | Which JS SoundFont synth and which `.sf2`? | See B-01. Library must be proposed and approved (CLAUDE.md rule 6). | B-01 |
| D2 ❓ | What does "Duplicate section" do? | (a) new instance of the same section, edits apply everywhere (current model); (b) independent copy; (c) both, as two commands. | B-10 |
| D3 ❓ | How should bass/harmony follow chord changes? | More candidates (N=8); bar-by-bar generation with per-bar masks (slower); higher CT weight for bass; stronger chord context. | B-20 |
| D4 ❓ | What is "Regenerate with note" (CLAUDE.md §8)? | Free-text hint mapped to controls (density, register…) or passed to the LLM planner. | B-16 |
| D5 ❓ | Should the master export include muted tracks? | Today: yes (mute = playback state only). Alternative: skip muted, or ask at export. | B-36 |

## P1 — next up

| ID | Item | Status | Notes |
|---|---|---|---|
| B-01 | **Realistic GM playback with a SoundFont** (replaces Tone.js timbres) | ❓ D1 | Play each track with its GM program, drums with the GM kit. Candidate libraries to evaluate: a JS SF2 synth on AudioWorklet (e.g. *spessasynth_lib*) or FluidSynth compiled to WASM (e.g. *js-synthesizer*). Candidate SoundFonts: *GeneralUser GS*, *FluidR3_GM*, *MuseScore General* (check licences and size). The `.sf2` is downloaded on demand (like model weights) and never committed if large; vendor the JS as a prebuilt file in `web/vendor/`. Keep Tone.js only if still useful for the transport. |
| B-10 | Section commands in the timeline: rename, duplicate (per D2), delete instance, insert a new section at a position | ❓ D2 | API exists: `PATCH /sections/{id}`, `PUT /projects/{id}/arrangement`, `DELETE /sections/{id}`. |
| B-11 | Drag section blocks to reorder | ⬜ | `PUT /projects/{id}/arrangement`. |
| B-12 | Lock / unlock a part in the UI | ⬜ | API exists (`PATCH /clips/{id}` `locked`). Locked parts are never regenerated and always used as context. |
| B-13 | **Vary**: `POST /generate/vary` + button | ⬜ | Next-best candidate from the last generation; candidates already kept in memory (`app.state.candidates`). |
| B-14 | **History**: versions list in the UI + `POST /clips/{id}/restore/{version_id}` | ⬜ | `GET /clips/{id}/versions` exists; restore endpoint missing. |

## P2 — soon

| ID | Item | Status | Notes |
|---|---|---|---|
| B-15 | **Replace**: set a part to another existing clip | ⬜ | Endpoint missing. |
| B-16 | Regenerate with note | ❓ D4 | |
| B-17 | Clip editor: piano roll on canvas (pan/zoom, draw/move/resize/delete, snap to 16th) | ⬜ | Saves a `manual` version via `PATCH /clips/{id}` `notes`. 60 fps for 64 bars × 6 tracks. |
| B-18 | Drum step grid for drum tracks | ⬜ | `core/drums.py` has grid ↔ notes. |
| B-19 | M4 acceptance: full replace / move / assemble flow without reload | ⬜ | |
| B-20 | Bass and harmonic parts follow chord changes | ❓ D3 | Today CT ≈ 0.5 on Am–F–C–G; best bass is often a pedal on the tonic. |
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

## M5 — work items

| ID | Item | Status |
|---|---|---|
| B-40 | `POST /import/midi`: import a `.mid` as clips (context or content) | ⬜ |
| B-41 | `RuleBasedPlanner` behind the `Planner` interface; `LLMPlanner` optional, off unless configured | ⬜ |
| B-42 | `scripts/benchmark_models.py` (stub today): mean S and latency per model over 20 runs; `make bench` | ⬜ |

## M6 — work items

| ID | Item | Status |
|---|---|---|
| B-50 | GitHub Actions matrix (ubuntu / macos / windows): lint + tests | ⬜ |
| B-51 | PyInstaller build per OS with a pywebview window; weights never bundled (licence) | ⬜ |

## Done (recent)

- ✅ M3 accepted: playback audible in the browser (user check, 2026-11-26).
- ✅ Timeline arrangement view: tracks as rows, time left → right, sections as bar blocks, zoom, playhead (`5c3dad5`).
- ✅ Vanilla web UI, Tone.js vendored, `.mid` export (`5ec6d71`, `e683d31`, `75b8baf`).
- ✅ Track-level `pitch_mask` fix (per-bar masks were ignored by midigpt) with regression tests (`2453a5c`).
