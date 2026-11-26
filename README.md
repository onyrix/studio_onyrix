# Studio Onyrix

Self-hosted AI MIDI composer: build a song part by part (drums, bass, chords, lead) in a simple web UI, export standard `.mid` files. Personal, non-commercial use.

Requirements and architecture live in [CLAUDE.md](CLAUDE.md).

## Quick start

Python 3.10–3.12 required. No Node.js needed: the web UI is plain HTML/CSS/JS served by FastAPI.

Windows:

```powershell
.\tasks.ps1 setup
.\tasks.ps1 migrate
.\tasks.ps1 run      # http://127.0.0.1:8000
```

macOS / Linux:

```bash
make setup && make migrate && make run
```

Other targets: `dev`, `test`, `test-infer`, `lint`, `fetch-models`, `bench`.
