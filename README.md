# Studio Onyrix

Version: `0.70`

Studio Onyrix is a config-driven MIDI song generator. It creates complete multi-track songs from musical intent: style, mood, BPM, chords, instruments, title, and prompt.

## Core Flow

- `generation/music_config.py`: central library for styles, moods, instruments, chord theory, song sections, and drum notes.
- `generation/song_config.py`: user-facing song request model.
- `generation/composer.py`: deterministic humanized MIDI composer.
- `generation/cli.py`: command-line entry point.
- `generation/batch.py`: powerful batch song generator for presets or style/mood matrices.
- `api/routes.py`: FastAPI endpoints for generation and configuration discovery.

`daw_core/` is intentionally kept as the future home for arrangement/timeline abstractions.

## Generate One Song

```powershell
.\.venv\Scripts\python.exe -m generation.cli --title "Night Bloom" --style rnb --mood luxury --bpm 92 --chords Cm9,Abmaj7,Ebmaj7,G7 --tracks drums,bass,electric_piano,pad,lead --bars 32 --prompt "silky keys, human late night groove" --output output\night_bloom.mid
```

## Generate Songs Batch

Windows:

```powershell
.\scripts\generate_songs.ps1 -OutputDir output\generated_songs -Bars 32
```

Linux/macOS:

```bash
bash scripts/generate_songs.sh output/generated_songs 32
```

Generate a style/mood matrix:

```powershell
.\scripts\generate_songs.ps1 -OutputDir output\matrix -Bars 16 -Mode styles -Styles "house,rnb,drum_and_bass" -Moods "euphoric,luxury,tense"
```

Preview without writing files:

```powershell
.\.venv\Scripts\python.exe -m generation.batch --mode all --limit 8 --dry-run
```

## Inspect Available Config

```powershell
.\.venv\Scripts\python.exe -m generation.cli --list-config
```

## API

Run:

```powershell
.\.venv\Scripts\uvicorn.exe api.server:app --reload
```

Useful endpoints:

- `GET /config`: project version, available styles, moods, and instruments.
- `POST /generate`: create one full MIDI song from a JSON song request.
