# Audio playback: SoundFont synth and banks (research for D1 / B-01)

Requirement from the user (2026-11-26): **maximum quality**, and the ability to **import other sound banks** downloaded by the user. Open-source libraries only. Tone.js built-in synths are judged insufficient.

## Synth engine (browser, no Node, no build)

| | SpessaSynth (`spessasynth_lib` + `spessasynth_core`) | js-synthesizer (FluidSynth → WASM) |
|---|---|---|
| Licence | Apache-2.0 (both packages) | BSD-3-Clause wrapper + **LGPL-2.1** libfluidsynth build |
| Formats | SF2, SF3 (Vorbis), SF2Pack/sfogg, DLS; reads/writes MIDI | SF2; SF3 only with the libsndfile build |
| Implementation | Pure JS/TS, AudioWorklet (or Worker) | Emscripten build of FluidSynth |
| Built-in sequencer | Yes (`Sequencer`: plays a MIDI file, loop, seek, current time) | Yes (FluidSynth player) |
| Version checked | lib 4.4.10, core 4.4.12 | — |
| Vendoring without a bundler | `dist/index.js` (ESM, imports `spessasynth_core`) + `dist/spessasynth_processor.min.js` (self-contained worklet, ~840 KB); core needs `fflate` and `stb-vorbis` → serve as ES modules resolved with a native `<script type="importmap">` | Single JS + WASM files |

**Recommendation: SpessaSynth.** Permissive licence end to end, SF2/SF3/DLS support (so users can import almost any free bank), active maintenance, and a built-in MIDI sequencer: we can play exactly the `.mid` that the server exports, so the browser hears the same file the DAW will get. FluidSynth is the reference sound engine, but brings an LGPL binary and weaker SF3 support for no clear gain here.

## Sound banks

| Bank | Licence (as found) | Size | Notes |
|---|---|---|---|
| **MuseScore General** (S. Christian Collins, from FluidR3) | MIT | SF3 ≈ 38 MB, SF2 ≈ 200 MB; an HQ SF3 exists | Clear licence: **default bank**, downloaded on first use / by `make fetch-soundfont`. |
| **GeneralUser GS 2.0** (S. Christian Collins) | GeneralUser GS License v2.0 (permissive, usable and modifiable in software; author cannot guarantee every sample's origin) | ≈ 30 MB | Very balanced GM/GS bank; offered as an optional download. |
| **FluidR3_GM** (Frank Wen) | MIT | ≈ 140 MB | Long-standing reference GM bank; optional download. |
| **Timbres of Heaven** (Don Allen) | Non-commercial; **no redistribution** without permission | ≈ 400 MB | Often rated among the best GM/GS banks. Personal use fits this project, but it must be **downloaded by the user** and imported; we never host or bundle it. |
| **Arachno 1.0** | Not verified | ≈ 148 MB | Check the licence before suggesting it. |

Rules (consistent with CLAUDE.md §1 rule 5 and §11): banks are never committed; they live in a git-ignored data folder; the app downloads only banks whose licence allows it, and everything else goes through user import.

## Proposed design (B-01)

1. **Bank storage (backend):** `data/soundfonts/` (git-ignored). Endpoints: `GET /api/soundfonts` (list with size and source), `POST /api/soundfonts` (upload `.sf2/.sf3/.dls`), `GET /api/soundfonts/{id}` (serve the file), `DELETE /api/soundfonts/{id}`; the active bank is a setting. `make fetch-soundfont` downloads MuseScore General.
2. **Playback (frontend):** vendor SpessaSynth in `web/vendor/spessasynth/` with an import map; load the active bank into the synth; play the **server-exported MIDI** for the selected section or the whole arrangement (needs a section-range export, e.g. `GET /api/export/project/{id}.mid?from=&to=`) through the SpessaSynth `Sequencer`; loop and playhead from the sequencer; mute/solo by muting MIDI channels (channel layout identical to `app/midi_io.py`: drums on channel 10).
3. **Import UI:** a "Suoni" dialog to upload a bank, pick the active one, and see licence notes for the suggested downloads.
4. Remove Tone.js once SpessaSynth covers transport and playback.

## Sources

- spessasynth_lib: https://github.com/spessasus/spessasynth_lib · README: https://unpkg.com/spessasynth_lib@3.25.16/README.md · core: https://github.com/spessasus/spessasynth_core
- js-synthesizer: https://npmjs.com/package/js-synthesizer · externals licence: https://app.unpkg.com/js-synthesizer@1.11.0/files/externals/README.md
- MuseScore SoundFont handbook (MuseScore General MIT, FluidR3, Arachno size): https://musescore.org/en/handbook/soundfonts
- MuseScore General licence: https://src.fedoraproject.org/rpms/mscore/blob/f36/f/MuseScore_General_License.md
- GeneralUser GS 2.0 licence: https://scancode-licensedb.aboutcode.org/generaluser-gs-2.0.LICENSE
- Timbres of Heaven terms (forum quotes, check the Readme): https://musescore.org/en/node/44941
- FluidSynth SoundFont list: https://www.github.com/FluidSynth/fluidsynth/wiki/SoundFont
