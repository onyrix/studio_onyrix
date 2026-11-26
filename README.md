# Studio Onyrix

Self-hosted AI MIDI composer: build a song part by part (drums, bass, chords, lead) in a simple web UI, export standard `.mid` files. Personal, non-commercial use.

Requirements and architecture live in [CLAUDE.md](CLAUDE.md).

## Quick start

Python 3.10–3.12 required. No Node.js needed: the web UI is plain HTML/CSS/JS served by FastAPI.

Windows:

```powershell
.\tasks.ps1 setup
.\tasks.ps1 migrate
.\tasks.ps1 fetch-soundfont   # default sound bank, MuseScore General (MIT), ~40 MB
.\tasks.ps1 run               # http://127.0.0.1:8000
```

macOS / Linux:

```bash
make setup && make migrate && make fetch-soundfont && make run
```

Other targets: `dev`, `test`, `test-infer`, `lint`, `fetch-models`, `bench`.

## Sounds

Playback uses SpessaSynth with a SoundFont/DLS bank. The default bank (MuseScore General) can also be downloaded from the **♫** button in the app; any other `.sf2/.sf3/.dls` you download can be imported there. Banks stay in `data/soundfonts/` and are never committed. Check each bank's licence: some are for non-commercial use only.
