# Studio Onyrix v4 - AI-Powered DAW Music Production

**Studio Onyrix v4** is a professional AI-powered DAW (Digital Audio Workstation) for music producers. Instead of generating full songs from vague prompts, it lets you build tracks **part by part** — like a real DAW — with precise musical control over every element.

🎵 **Generate individual instrument parts** with exact BPM, key, scale, division, and measures. Build your song track by track.

---

## 🚀 Key Concepts

| Concept | Description |
|---------|-------------|
| **PART** | A single instrument part (e.g., "808 bass for 8 bars in C minor") |
| **PROJECT** | Collection of parts forming a complete song |
| **MEMORY** | Coherence system that tracks what was generated for musical consistency |
| **PROMPT ENGINEERING** | Builds precise musical prompts from your parameters |
| **MIX** | Combines all parts into a final stereo master |

---

## 🏗️ Architecture

```
User defines a PART:
  BPM: 140, Division: 4/4
  Root: C, Scale: natural_minor
  Measures: 8
  Instrument: 808_bass
  Relation: verse
  Volume: 0.8, Pan: 0.0
      ↓
  [DAWPartGenerator]
  Builds precise prompt with musical context
      ↓
  [MusicGen (Meta)] - State-of-the-Art AI
      ↓
  32kHz WAV Audio + librosa Analysis (tempo, beats, pitch)
      ↓
  Part saved to PROJECT with MEMORY
      ↓
  Mix all parts → Final master WAV
```

---

## 📦 Installation

### Prerequisites
- **Python 3.10+** (64-bit recommended)
- **pip** (Python package manager)
- **GPU Recommended**: For MusicGen `large` model (CPU works for `small`)

### Quick Install
```bash
# Core dependencies
pip install numpy soundfile

# Modern AI - MusicGen (required for generation)
pip install transformers torchaudio

# Audio analysis
pip install librosa

# Optional: Full test
python main.py
```

---

## 🎯 Usage

### Interactive Mode (Recommended)
```bash
python main.py
```
Opens an interactive shell where you can:
```
[My Song] > new My New Track
[My Song] > add --preset bass --bpm 140 --root C --scale natural_minor
[My Song] > add --preset drums --bpm 140
[My Song] > add --preset chords --root C --scale natural_minor
[My Song] > mix
[My Song] > save my_track.json
```

### Command Line
```bash
# Create a new project
python main.py new "My Track"

# Add a bass part (with full control)
python main.py part \
  --instrument 808_bass \
  --bpm 140 \
  --division 4/4 \
  --root C \
  --scale natural_minor \
  --measures 8 \
  --relation verse \
  --volume 0.8 \
  --pan 0.0 \
  --temperature 1.0
  --gen true

# Add parts using presets
python main.py part --preset drums --bpm 140
python main.py part --preset chords --root C --scale natural_minor
python main.py part --preset melody --bpm 140 --root C --scale natural_minor

# Manage project
python main.py list          # List all parts
python main.py info 0        # Show part 0 details
python main.py remove 1      # Remove part 1
python main.py show          # Project summary

# Mix all parts to audio
python main.py mix

# Save/Load
python main.py save my_song.json
python main.py load my_song.json

# Explore
python main.py instruments   # List all available instruments
python main.py scales        # List all scale patterns
```

---

## 🎸 Available Instruments

### Bass
| Instrument | Description | BPM Range |
|------------|-------------|-----------|
| `808_bass` | Deep subby 808 bass, sustained | 60-160 |
| `sub_bass` | Clean sine wave sub bass | 60-140 |
| `pluck_bass` | Electric bass guitar, attacky | 80-180 |
| `synth_bass` | Analog synth bass, filter sweep | 100-160 |

### Drums
| Instrument | Description | BPM Range |
|------------|-------------|-----------|
| `kick` | Punchy kick drum | 60-200 |
| `snare` | Crisp snare drum | 60-200 |
| `hi_hat` | Tight hi-hat pattern | 80-200 |
| `drums_full` | Full drum kit | 60-180 |
| `trap_drums` | 808 kicks, hi-hat rolls | 130-170 |
| `techno_drums` | Four-on-the-floor, clap | 120-150 |
| `dnb_drums` | Fast breaks, intricate | 165-180 |

### Chords / Keys
| Instrument | Description | BPM Range |
|------------|-------------|-----------|
| `piano` | Acoustic grand piano | 60-160 |
| `synth_pad` | Warm analog synth pad | 60-140 |
| `organ` | Hammond organ | 60-140 |
| `wurlitzer` | Vintage electric piano | 60-130 |

### Melody / Lead
| Instrument | Description | BPM Range |
|------------|-------------|-----------|
| `synth_lead` | Monophonic synth lead | 80-180 |
| `violin` | Orchestral violin | 60-140 |
| `flute` | Airy flute melody | 60-140 |
| `guitar_melody` | Electric guitar lead | 60-160 |

### Arpeggio
| Instrument | Description | BPM Range |
|------------|-------------|-----------|
| `arp` | Synthesizer arpeggio | 100-170 |
| `pluck_arp` | Plucked synth arpeggio | 100-160 |

### FX
| Instrument | Description | BPM Range |
|------------|-------------|-----------|
| `riser` | Rising tension builder | 60-200 |
| `noise_sweep` | White noise transition | 60-200 |
| `texture_pad` | Ambient texture | 40-100 |

---

## 🎼 Available Scales

### Major/Minor
- `major`, `natural_minor`, `harmonic_minor`, `melodic_minor`

### Modes
- `dorian`, `phrygian`, `lydian`, `mixolydian`, `aeolian`, `locrian`

### Pentatonic/Blues
- `major_pentatonic`, `minor_pentatonic`, `blues`

### Symmetrical
- `chromatic`, `whole_tone`, `diminished`

---

## 📁 Part Parameters (DAWPart)

Every part you generate has these professional DAW controls:

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `bpm` | 120 | 30-300 | Tempo in BPM |
| `division` | 4/4 | 2/2,3/4,4/4,5/4,6/8,7/8,12/8 | Time signature |
| `root` | C | C,C#,D,...,B | Tonic/root note |
| `scale` | natural_minor | all 17 scales | Scale pattern |
| `measures` | 8 | 1+ | Number of bars |
| `instrument` | synth_pad | any from list | Instrument preset |
| `relation` | verse | intro,verse,chorus,bridge,drop,build,fill,outro | Section type |
| `volume` | 0.8 | 0.0-1.0 | Track volume |
| `pan` | 0.0 | -1.0 to 1.0 | Stereo pan |
| `temperature` | 1.0 | 0.5-1.5 | AI creativity |
| `extra` | "" | any text | Extra prompt instructions |

---

## 🧠 How It Works

### Prompt Engineering
When you add a part, the system builds a precise prompt:
```
Generate a deep subby 808 bass, sustained, heavy low end part for music production.
Time signature: 4/4.
Tempo: 140 BPM.
Length: 8 bars (13.7 seconds).
Key: C natural minor.
Scale notes: C, D, D#, F, G, G#, A#.
Section: verse section, supporting the narrative.
Instrument register: low.
```

### Memory System
The DAWMemory tracks all generated parts and provides contextual prompts:
```
Existing instruments: 808_bass.
Previous verse had 808_bass in C natural minor at 140 BPM.
This is part 2 in the project.
```

### Audio Analysis
After generation, librosa extracts:
- **Tempo detection** (checks if MusicGen followed your BPM)
- **Beat positions** (for future quantization)
- **Pitch analysis** (key/scale estimation)
- **Spectral features** (timbre classification)

### Mixing
The DAWMixer combines all parts with:
- Volume per track
- Stereo panning
- Timeline alignment (order determines arrangement)
- Normalization

---

## 📁 Project Files

Projects are saved as JSON files:
```json
{
  "project": {
    "name": "My Track",
    "bpm": 140,
    "division": "4/4",
    "root": "C",
    "scale": "natural_minor"
  },
  "parts": [
    {
      "instrument": "808_bass",
      "bpm": 140,
      "root": "C",
      "scale": "natural_minor",
      "measures": 8,
      "relation": "verse",
      "volume": 0.8,
      "pan": 0.0,
      "audio_path": "output/808_bass_verse_223543_223905.wav",
      "duration": 6.9,
      "analysis": {"tempo": 138.9, ...}
    }
  ]
}
```

---

## 💻 Programmatic Usage

```python
from daw_engine import DAWProject, DAWPart, DAWPartGenerator

# Create a project
project = DAWProject(name="My Track", bpm=140, root="C", scale="natural_minor")

# Create a bass part
bass_part = DAWPart(
    instrument="808_bass",
    bpm=140,
    root="C",
    scale="natural_minor",
    measures=8,
    relation="verse",
    volume=0.8,
    pan=0.0,
    temperature=0.6,
)
project.add_part(bass_part)

# Generate audio
generator = DAWPartGenerator(model_size='small')
result = generator.generate_part(bass_part)

# Add more parts
drum_part = DAWPart(instrument="trap_drums", bpm=140, measures=8, relation="verse")
project.add_part(drum_part)
result2 = generator.generate_part(drum_part)

# Mix
from daw_engine import DAWMixer
mixer = DAWMixer()
mixer.mix_project(project)

# Save project
project.save("my_track.json")
```

---

## 📁 Project Structure

```
studio_onyrix/
├── main.py                  # CLI entry point (DAW commands)
├── daw_engine.py            # Core DAW: DAWPart, DAWProject, DAWPartGenerator, DAWMemory, DAWMixer
├── modern_ai_generator.py   # MusicGen backend (Audio generation)
├── requirements.txt         # Dependencies
├── README.md                # This file
│
├── output/                  # Generated audio + project files
│   ├── project.json         # Current project
│   ├── *.wav                # Individual part audio
│   └── *mix.wav             # Final mixed master
│
├── docs/                    # Documentation
└── (legacy files: removed)
```

---

## 🗑️ Legacy Files Removed

The following MIDI-based files have been deprecated and removed:
- `ai_midi_generator.py` - MidiBERT/MMM AI (weak)
- `ai_prompt_parser.py` - Ollama prompt parser (obsolete)
- `drums_bass.py`, `harmonic_engine.py`, `melody_engine.py` - MIDI generators
- `audio_render.py` - MIDI-to-audio synth
- `style_library.py`, `style_engine.py` - Style templates
- `global_memory.py`, `utils.py` - MIDI utilities

All replaced by `modern_ai_generator.py` + `daw_engine.py`.

---

## 🚀 Roadmap

- **Loop Mode**: Repeat parts for verse/chorus structure
- **MIDI Export**: Convert audio analysis to MIDI for editing
- **Effects**: Real-time reverb, delay, compression
- **Stem Separation**: Isolate generated parts into stems
- **GUI**: PyQt/Tkinter DAW interface
- **Multi-GPU**: Parallel part generation
- **Audio Conditioning**: Start from audio reference

---

## 📝 Notes

- MusicGen-small model (~300MB) auto-downloads on first use
- GPU recommended for MusicGen-large (3GB)
- CPU works for MusicGen-small (slower, ~30s for 15s audio)
- All processing is LOCAL - zero cloud costs
- Model cache: `~/.cache/huggingface/hub/`

---

**Studio Onyrix v4** - Build your music. One part at a time. 🎵