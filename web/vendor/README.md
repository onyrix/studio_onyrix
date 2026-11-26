# Vendored third-party code

Prebuilt files served as-is (no build step, no CDN at runtime). Update by replacing the files and this table.

| Library | Version | File | Source | SHA-256 | Licence |
|---|---|---|---|---|---|
| spessasynth_lib | 4.4.10 | `spessasynth/spessasynth_lib.js` | https://cdn.jsdelivr.net/npm/spessasynth_lib@4.4.10/dist/index.js | `EEE966E9170A9656B68368C5C578FA248D345195A9867722B6F676B446A4B7D6` | Apache-2.0 (`spessasynth/LICENSE-*`) |
| spessasynth_lib (worklet) | 4.4.10 | `spessasynth/spessasynth_processor.min.js` | https://cdn.jsdelivr.net/npm/spessasynth_lib@4.4.10/dist/spessasynth_processor.min.js | `5D82C847809F42C7EC2683028DDFB140B1AFE0B07E1630A360967CC7968078BE` | Apache-2.0 (`spessasynth/LICENSE-*`) |
| spessasynth_core | 4.4.12 | `spessasynth/spessasynth_core.js` | https://cdn.jsdelivr.net/npm/spessasynth_core@4.4.12/dist/index.js | `5BE9455952B0651435F5FFEEBE5D65289E65D34ABB13E1168308241BB2C4656D` | Apache-2.0 (`spessasynth/LICENSE-*`) |
| fflate | 0.8.3 | `spessasynth/fflate.js` | https://cdn.jsdelivr.net/npm/fflate@0.8.3/esm/browser.js | `B7CA4450B19559A1D50EB381ADCEE94B82449674BE4CD17789D9BEBA7E6122A1` | MIT (`spessasynth/LICENSE-*`) |
| stb-vorbis | 0.0.8 | `spessasynth/stb-vorbis.js` | https://cdn.jsdelivr.net/npm/stb-vorbis@0.0.8/dist/index.js | `A8F0833C061AA71A71DD03F26151790E4DDF38D3C07DB6EF7F9CC0A9C8AB0C1E` | Apache-2.0 (`spessasynth/LICENSE-*`) |

SpessaSynth modules import bare specifiers (`spessasynth_core`, `fflate`, `stb-vorbis`); `web/index.html` resolves them with a native `<script type="importmap">`.
