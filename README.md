# Studio Onyrix v0.5

Studio Onyrix is becoming a parametric AI DAW project engine. The current v0.5 focus is not a polished UI yet: it is the project format and export pipeline that a future DAW interface can sit on top of.

The engine can create a full song project with separated tracks, a source-of-truth JSON document, a master MIDI file, per-track MIDI files, and a WAV preview.

## Core Idea

Studio Onyrix treats a song as a DAW project:

- `DAWProject`: global tempo, key, scale, groove, arrangement memory and render settings
- `DAWTrack`: mixer/timeline lane such as drums, bass, chords, lead or FX
- `DAWPart`: a clip placed on a track at a bar position
- `assets`: exported MIDI/WAV files referenced by the project JSON
- `memory`: prompts, generation history, section roles and warnings

The JSON is the future UI contract. A DAW UI should be able to load it and rebuild the song timeline.

## Quick Start

Install the lightweight local dependencies:

```powershell
pip install -r requirements.txt
```

Generate a complete parametric song:

```powershell
python main.py compose --style trap --name TrapNoir --output output/songs/trap_noir
```

Outputs:

```text
output/songs/trap_noir/project.json
output/songs/trap_noir/song.mid
output/songs/trap_noir/song.wav
output/songs/trap_noir/midi_tracks/drums.mid
output/songs/trap_noir/midi_tracks/bass.mid
output/songs/trap_noir/midi_tracks/chords.mid
output/songs/trap_noir/midi_tracks/lead.mid
output/songs/trap_noir/midi_tracks/fx.mid
```

List available full-song styles:

```powershell
python main.py styles
```

Current presets:

- `trap`
- `synthwave`
- `lofi`
- `rock`

## Compose Flags

```powershell
python main.py compose --style synthwave --name Neon --bpm 104 --root D --scale natural_minor --chords "Dm Bb F C" --measures 32 --output output/songs/neon
```

Supported flags:

- `--style`: style preset
- `--name`: project name
- `--bpm`: override tempo
- `--root`: override root note
- `--scale`: override scale
- `--chords`: override chord progression
- `--measures`: scale the arrangement to a target bar count
- `--output`: export directory

## Manual Project Commands

You can still build part by part:

```powershell
python main.py new MyTrack --bpm 140 --root A --scale natural_minor
python main.py arrangement --chords "Am F C G" --groove trap --swing 0.12 --style "trap dark"
python main.py add --preset drums --track drums --start 1 --measures 8 --generate false
python main.py add --preset bass --track bass --start 1 --measures 8 --generate false
python main.py list
python main.py json output/my_track.json
```

## Project JSON v0.5

The exported JSON has these top-level sections:

- `schema_version`
- `project`
- `transport`
- `musical_context`
- `render_settings`
- `master`
- `tracks`
- `parts`
- `assets`
- `memory`

Important asset scopes:

- `master` MIDI: one importable MIDI file with all tracks
- `track` MIDI: one MIDI file per instrument lane
- `audio`: WAV preview reference

## MIDI and WAV Export

`v05_renderer.py` provides an offline deterministic renderer. It is intentionally simple:

- It does not require MusicGen.
- It writes a standard `.mid` master file.
- It writes separated `.mid` files per track.
- It writes a basic `.wav` preview so tests and UI prototypes have something audible.

The WAV preview is not the final sound design layer. It is a reliable transport/export check while the MIDI generation and instrument mapping are improved.

## Tests

Run the current v0.5 export test:

```powershell
python -m unittest test_v05_exports.py
```

The test creates four songs:

- `trap_noir`
- `neon_synthwave`
- `lofi_sunset`
- `garage_rock`

Each test song must export:

- `project.json`
- `song.mid`
- `song.wav`
- per-track MIDI files

## Code Layout

```text
main.py              CLI entry point
daw_engine.py        Core project, track, part, memory, mixer and MusicGen integration
v05_song_factory.py  Parametric full-song factory and style presets
v05_renderer.py      Offline MIDI/WAV exporter
modern_ai_generator.py Optional MusicGen backend
test_v05_exports.py  Export pipeline tests
docs/                Install/run notes
output/              Generated projects and assets
```

## Roadmap

Next useful steps:

- Improve MIDI generation with editable note-level structures per part.
- Add richer instrument maps and explicit GM/program metadata.
- Make per-part MIDI assets, not only per-track stems.
- Add effect chains and automation lanes to the JSON contract.
- Build the first DAW UI around `project.json`.
- Optionally use MusicGen as a high-quality audio render layer once the musical project data is solid.
