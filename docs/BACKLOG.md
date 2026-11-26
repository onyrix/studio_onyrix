# Backlog

Single source of truth for what is done, what is next and what is undecided. Milestones and acceptance criteria are defined in `CLAUDE.md` §10; this file tracks their status and the concrete work items. Update it in the same commit that completes or changes an item.

Last review: 2026-11-26.

Legend: ✅ done · 🟡 partly done / acceptance pending · ⬜ to do · ❓ needs a decision

## Milestone status

| # | Scope | Status | Notes |
|---|---|---|---|
| M0 | Repo, tooling, schema + Alembic, core model + timebase | ✅ | `make test` green; schema migrates from empty (`tests/db`). |
| M1 | Model spike | ✅ | `scripts/m1_spike.py`, findings in `docs/midigpt-notes.md`. |
| M2 | Adapter, engine, candidates, scorer, post-processing, `/generate` + SSE | ✅ | 4 candidates, best by S, same seed ⇒ same notes, also with the real model (`tests/inference/test_api_generate.py`). |
| M3 | Vanilla frontend: arrangement, transport, playback, export | 🟡 | Built and checked headless (rendering, generate + SSE, scheduling, export). **Acceptance pending:** "a generated 8-bar loop is audible in the browser" must be confirmed by ear (headless Chrome's audio clock does not advance). |
| M4 | Clip editor, replace / vary / lock / history, section reorder + duplicate | ⬜ | Next. Items below. |
| M5 | Import `.mid`, rule-based planner, benchmark | ⬜ | |
| M6 | Packaging (PyInstaller, pywebview, CI matrix) | ⬜ | |

## Open decisions

| ID | Question | Options | Blocks |
|---|---|---|---|
| D1 ❓ | SoundFont playback: which JS SF2 synth and which `.sf2` file? | Library to propose (rule 6); SF2 with a redistributable licence, downloaded on demand and not committed if large. Today: Tone.js built-in synths per role. | Realistic GM sound (not M3 acceptance) |
| D2 ❓ | What does "Duplicate section" do? | (a) new instance of the same section, edits apply everywhere (current CLAUDE.md model); (b) independent copy; (c) both as two commands. | M4 section commands |
| D3 ❓ | How to make bass/harmony follow chord changes? | More candidates (N=8); bar-by-bar generation with per-bar masks (slower); higher CT weight for bass; stronger chord context track. | Musical quality |
| D4 ❓ | What is "Regenerate with note" (CLAUDE.md §8)? | Free-text hint mapped to controls (density, register…) or passed to the LLM planner. Needs a definition before implementing. | M4 cell actions |

## M3 — remaining

- 🟡 Confirm audible playback and the moving playhead in a real browser (play section, loop, play all, mute/solo).

## M4 — work items

Arrangement / sections (timeline):
- ⬜ Section header actions: rename, delete instance, duplicate (per D2), insert new section at a position.
- ⬜ Drag section blocks to reorder (API exists: `PUT /projects/{id}/arrangement`).
- ⬜ Remove one instance without deleting the section (front end only, via `PUT …/arrangement`).

Parts (clips):
- ⬜ Lock / unlock toggle on a part (API exists: `PATCH /clips/{id}` `locked`); locked parts never regenerate and always act as context.
- ⬜ **Vary**: `POST /generate/vary` returns the next-best candidate from the last generation (candidates already kept in memory in `app.state.candidates`).
- ⬜ **History**: list versions in the UI (`GET /clips/{id}/versions` exists) and `POST /clips/{id}/restore/{version_id}` (missing).
- ⬜ **Replace**: set a slot to another existing clip (endpoint missing).
- ⬜ Regenerate with note (per D4).

Clip editor:
- ⬜ Piano roll on canvas: pan/zoom, draw/move/resize/delete, snap to 16th; saves a `manual` version (`PATCH /clips/{id}` `notes` exists).
- ⬜ Drum step grid for drum tracks (`core/drums.py` has grid ↔ notes).

Acceptance: full replace / move / assemble flow works without reload.

## M5 — work items

- ⬜ `POST /import/midi`: import a `.mid` as clips (as context or content).
- ⬜ `RuleBasedPlanner` (chord grid and sections per mode/genre) behind the `Planner` interface (`app/gen/planner.py`); `LLMPlanner` optional, off unless configured.
- ⬜ `scripts/benchmark_models.py` (stub today): mean S and latency per model over 20 runs; `make bench`.

## M6 — work items

- ⬜ GitHub Actions matrix (ubuntu / macos / windows): lint + tests.
- ⬜ PyInstaller build per OS, pywebview window; weights never bundled (licence).

## Known gaps and tech debt

Generation:
- ⬜ Context from **neighbouring sections** within the model window (CLAUDE.md §6.1) is not used: only other parts of the same section are context.
- ⬜ Sections longer than the largest window (16 bars prism, 8 yellow) rely on the library's windowing; not tested with the real model, and the "2 bars overlap, earlier window wins" rule is not verified.
- ⬜ Triplet grid and humanize exist in `core/postprocess.py` but are not exposed as project/generation settings.
- ⬜ First candidate's notes are not streamed over SSE (optional in CLAUDE.md §7).
- ⬜ In-memory candidate store is lost on restart (acceptable for "Vary" within a session; document in the UI).

Front end:
- ⬜ No delete for projects / tracks / sections in the UI (API exists).
- ⬜ Time signature not editable in the UI (API and export support it).
- ⬜ No dev mode with a fake engine for UI work without loading the model.

Export:
- ❓ Muted tracks are included in the master export (mute is treated as playback state). Confirm this is wanted.

## Done (recent)

- ✅ Timeline arrangement view: tracks as rows, time left → right, sections as bar blocks, zoom, playhead (`5c3dad5`).
- ✅ Vanilla web UI, Tone.js vendored, `.mid` export (`5ec6d71`, `e683d31`, `75b8baf`).
- ✅ Track-level `pitch_mask` fix (per-bar masks were ignored by midigpt) with regression tests (`2453a5c`).
