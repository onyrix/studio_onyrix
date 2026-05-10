# Studio Onyrix v2

**Studio Onyrix v2** is a hybrid AI + rule-based music generation system that creates MIDI compositions in 25+ styles. It combines **local pre-trained AI models** (MidiBERT, MMM, DiffMIDI) with a granular rule-based engine for full DAW-like control.

🎵 **Now with Local AI**: Generate music using natural language prompts, with zero cloud costs!

## 🚀 What's New in v2

- **Local AI Integration**: MidiBERT, Multi-Track Music Machine (MMM), DiffMIDI
- **Natural Language Prompts**: "Create a chill lofi track in G major" → Full MIDI arrangement
- **Hybrid Workflow**: AI seeds + rule-based refinements (humanization, style tweaks)
- **Zero Cloud Costs**: All AI models run locally on your machine
- **Enhanced Main Interface**: New `--ai` flag for AI generation mode

## 🎵 Core Features

- **Hybrid AI + Rule-Based Generation**: Best of both worlds - AI creativity + precise control
- **25+ Music Styles**: Trap, LoFi, Techno, Jazz, Rock, Synthwave, and more
- **Local AI Models**: MidiBERT (melodies), MMM (multi-track), DiffMIDI (drums/bass)
- **Natural Language Input**: Parse prompts with local LLMs (Ollama + Llama 3)
- **Granular DAW Control**: Every note editable via rule-based engine
- **Multi-Track Output**: Separate drums, bass, melody, pads, chords
- **MIDI + Audio**: Generate MIDI files and render to WAV
- **Memoria Tematica**: Motif evolution system for coherent compositions

## 🏗️ Architecture v2

```
User Prompt (Natural Language)
         ↓
    [AI Prompt Parser] → Ollama/Llama 3 (local LLM)
         ↓
    {style, key, mood, bpm, instruments}
         ↓
    ┌──────────────────────────────────────┐
    │     AI MIDI Generators (Local)        │
    │  • MidiBERT: Melodies & chords      │
    │  • MMM: Full multi-track MIDI       │
    │  • DiffMIDI: Drums & bass patterns  │
    └──────────────────────────────────────┘
         ↓
    [Hybrid Workflow] AI seeds + Rule-based editing
         ↓
    ┌──────────────────────────────────────┐
    │   Rule-Based Engines (Granular)      │
    │  • drums_bass.py: Rhythm & bass     │
    │  • melody_engine.py: Melodies       │
    │  • harmonic_engine.py: Chords       │
    │  • style_engine.py: Style params    │
    └──────────────────────────────────────┘
         ↓
    [Output] MIDI (.mid) + Audio (.wav)
         ↓
    [Future: DAW Interface for human editing]
```

## 📦 Installation

### Prerequisites
- **Python 3.10 or 3.11 (64-bit)** - Avoid 3.12+ (TensorFlow/Magenta incompatibility)
- **pip** (Python package manager)
- **Git** (for downloading model checkpoints)

### Step 1: Clone & Install Core Dependencies
```bash
git clone https://github.com/onyrix/studio_onyrix.git
cd studio_onyrix

# Install core dependencies
pip install pretty_midi mido numpy soundfile fluidsynth
```

### Step 2: Install AI Dependencies (Optional)
```bash
# PyTorch (required for MidiBERT, DiffMIDI)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# MidiBERT (melody generation)
pip install midibert-remi

# DiffMIDI (diffusion-based generation)
# Install from source: https://github.com/zbwang/diffmidi

# Magenta MMM (multi-track generation)
pip install magenta

# Ollama (local LLM for prompt parsing)
# Download from: https://ollama.com
# Then pull model:
ollama pull llama3.2:3b
```

### Step 3: Download AI Model Checkpoints
```bash
# Create checkpoints directory
mkdir checkpoints

# See download instructions
python -c "from ai_midi_generator import download_checkpoints; download_checkpoints()"
```

## 🎯 Usage

### Basic Generation (Rule-Based)
```bash
# Generate a trap track in F minor (default)
python main.py

# Generate in specific style
python main.py lofi D_major 0.2

# Use --ai flag for AI-enhanced generation
python main.py techno C_minor 0.5 --ai
```

### Natural Language Prompts
```python
from ai_prompt_parser import generate_from_prompt

# Generate from prompt
midi = generate_from_prompt("Create a chill lofi track in G major")
midi.write("output/my_lofi_track.mid")
```

### Command Line Options
```bash
# List all available styles
python main.py --list
# or
python main.py -l

# Generate with AI mode
python main.py trap C_minor 0.3 --ai

# Parameters:
#   1. style: Music style (trap, lofi, techno, etc.)
#   2. key: Musical key (C_major, F_minor, etc.)
#   3. chaos: Variation level 0.0-1.0 (default: 0.3)
#   4. --ai: Enable AI generation (if models available)
```

## 🤖 AI Models Available

### MidiBERT (Melody & Chord Generation)
- **Purpose**: Generate melodies and chord progressions
- **Model Size**: ~300MB
- **Pre-trained on**: 1.7M MIDI files
- **Usage**: `python main.py jazz C_major 0.3 --ai`

### MMM (Multi-Track Music Machine)
- **Purpose**: Full multi-track MIDI generation
- **Model Size**: ~1GB
- **Pre-trained on**: Lakh MIDI Dataset (176k+ files)
- **Output**: Separate tracks for drums, bass, melody, pads

### DiffMIDI (Diffusion-Based)
- **Purpose**: High-quality drum/bass patterns
- **Model Size**: ~500MB
- **Technology**: Diffusion probabilistic models
- **Quality**: State-of-the-art MIDI generation

### Ollama/Llama 3 (Prompt Parsing)
- **Purpose**: Convert natural language to music parameters
- **Model**: Llama 3.2 3B (fast, efficient)
- **Zero Cost**: Runs 100% locally

## 🎼 Available Music Styles (25+)

### Hip Hop / Urban
- **trap** (130-160 BPM) - Syncopated bass, complex rhythms
- **drill** (130-145 BPM) - Sliding bass, dark atmospheres
- **boom_bap** (80-100 BPM) - Swing drums, walking bass
- **lofi** (65-90 BPM) - Relaxed vibes, complex chords

### Club / Electronic
- **house** (118-130 BPM) - Four-on-the-floor, build/drop
- **deep_house** (118-122 BPM) - Dorian scales, groovy bass
- **techno** (125-140 BPM) - Repetitive patterns, phrygian mode
- **minimal_techno** (120-128 BPM) - Sparse, locrian mode
- **dubstep** (135-145 BPM) - Wobble bass, intense drops
- **dnb** (165-180 BPM) - Fast breaks, rolling bass

### Cinematic / Atmospheric
- **ambient** (40-80 BPM) - Ethereal soundscapes
- **cinematic** (60-100 BPM) - Orchestral arrangements
- **downtempo** (80-110 BPM) - Relaxed rhythms

### Band / Acoustic
- **rock** (90-140 BPM) - Classic structure, driving bass
- **funk** (95-120 BPM) - Syncopated rhythms, slap bass
- **jazz** (90-140 BPM) - Swing, walking bass, complex chords

### Synth / Retro / Electronic
- **synthpop** (100-120 BPM) - Melodic synths, pop structure
- **synthwave** (85-110 BPM) - 80s retro, arpeggiators
- **retrowave** (90-115 BPM) - Driving bass, retro vibes
- **outrun** (95-125 BPM) - Energetic, synth guitars
- **darkwave** (90-115 BPM) - Dark atmospheres, phrygian mode
- **ebm** (120-140 BPM) - Electronic Body Music, martial patterns
- **electro** (110-130 BPM) - Electro-funk, funky bass
- **idm** (90-160 BPM) - Experimental, chromatic scales
- **glitch** (70-130 BPM) - Irregular patterns, whole-tone scales
- **electronic_pop** (100-128 BPM) - Modern pop structure

## 📁 Project Structure v2

```
studio_onyrix/
├── main.py                    # Entry point with AI/hybrid support
├── ai_midi_generator.py      # NEW: AI models (MidiBERT, MMM, DiffMIDI)
├── ai_prompt_parser.py       # NEW: Natural language → music params
├── requirements.txt           # NEW: Updated dependencies
│
├── melody_engine.py          # Melody generation (rule-based)
├── harmonic_engine.py        # Chord progressions (rule-based)
├── drums_bass.py            # Drums & bass (rule-based + music theory)
├── style_engine.py           # Style parameter builder
├── style_library.py         # 25+ style definitions
├── global_memory.py         # Motif memory system
├── audio_render.py          # MIDI → WAV rendering
├── automation.py            # Parameter automation
├── utils.py                 # Music theory utilities
├── instrument_map.py        # MIDI instrument mappings
│
├── checkpoints/             # NEW: AI model checkpoints
│   ├── midibert-piano.ckpt
│   ├── mmm.ckpt
│   └── diffmidi.ckpt
│
├── output/                  # Generated MIDI and WAV files
├── docs/
│   └── install_and_run.txt
└── README.md               # This file (v2)
```

## 🧠 How Hybrid Generation Works

### AI Stage (Optional)
1. **Prompt Parsing**: Ollama/Llama 3 converts "chill lofi in G major" → `{style: "lofi", key: "G_major", ...}`
2. **AI Generation**:
   - MidiBERT generates melody and chord progressions
   - MMM creates full multi-track arrangement
   - DiffMIDI produces drum/bass patterns

### Rule-Based Stage (Always)
3. **Style Application**: Apply style-specific parameters (drum patterns, swing, etc.)
4. **Humanization**: Add timing jitter, velocity variation, ghost notes
5. **Refinement**: Adjust intensity per section, apply motif evolution

### Output
6. **MIDI File**: Editable in any DAW (Ableton, FL Studio, Logic, etc.)
7. **Audio Render**: Synthesized WAV file via FluidSynth

## 💻 Programmatic Usage

### Basic (Rule-Based)
```python
from main import generate_track_with_style

# Generate a jazz track
midi = generate_track_with_style("jazz", "D_minor", chaos=0.4)
midi.write("output/my_jazz_track.mid")
```

### With AI (Hybrid)
```python
from main import generate_track_with_style

# Generate with AI enhancement
midi = generate_track_with_style(
    style_name="trap",
    key="C_minor",
    chaos=0.3,
    use_ai=True  # Enable AI generation
)
midi.write("output/ai_trap_track.mid")
```

### Natural Language
```python
from ai_prompt_parser import generate_from_prompt

# Generate from prompt
midi = generate_from_prompt(
    "Create an aggressive techno track with heavy bass in F minor",
    use_ai=True
)
midi.write("output/my_techno_track.mid")
```

### Direct AI Model Access
```python
from ai_midi_generator import HybridMIDIGenerator

generator = HybridMIDIGenerator()

# Check available models
print(generator.available_models)
# {'midibert': True, 'mmm': True, 'diffmidi': True}

# Generate hybrid track
midi = generator.generate_hybrid(
    style="synthwave",
    key="A_minor",
    bpm=110,
    chaos=0.3,
    bars=16,
    use_ai=True
)
```

## 🔧 Development

### Adding a New Style
Edit `style_library.py` and add your style definition:
```python
"my_style": {
    "bpm_range": (120, 130),
    "drum_density": 0.7,
    "swing": 0.1,
    "patterns": {...},
    "scale_type": "natural_minor",
    "chord_complexity": 0.4,
    "bass_pattern": "driving",
    "melody_density": 0.5,
    "typical_progressions": [[0, 3, 4], [0, 5, 3]],
    "instruments": {
        "lead": "Lead 1 (square)",
        "pad": "Pad 1 (new age)",
        "bass": "Synth Bass 1"
    },
    "arrangement_template": [...]
}
```

### Extending AI Capabilities
Create custom AI pipelines in `ai_midi_generator.py`:
```python
class CustomAIGenerator:
    def generate_custom(self, prompt, **kwargs):
        # Your custom AI logic here
        pass
```

## 📝 Notes on AI Models

### System Requirements for AI
| Component | Minimum | Recommended |
|-----------|----------|-------------|
| **RAM** | 8GB | 16GB+ |
| **GPU** | None (CPU works) | NVIDIA GPU 4GB+ VRAM |
| **Storage** | 5GB (for models) | 10GB |
| **Python** | 3.10+ | 3.11 |

### Fallback Behavior
If AI models are not available, the system automatically falls back to rule-based generation:
```python
# This will use rule-based if AI models not installed
python main.py trap C_minor 0.3 --ai
# Output: "Warning: AI modules not installed. Using rule-based generation."
```

## 🤝 Contributing

We welcome contributions! Priority areas:
- **DAW Interface**: Build a GUI for granular editing
- **More AI Models**: Integrate MusicGen, AudioCraft
- **Vocal Generation**: Add lyric/melody synthesis
- **Effects Processing**: Reverb, delay, compression, EQ
- **Sample Support**: Load and manipulate audio samples

## 📄 License

Open-source project available for personal and commercial use.

## 🙏 Acknowledgments

- **Magenta Team** (Google) for MMM and music AI tools
- **MidiBERT Authors** for pre-trained melody models
- **DiffMIDI Authors** for diffusion-based MIDI generation
- **Ollama Team** for local LLM infrastructure
- **Pretty MIDI** library for MIDI manipulation
- **FluidSynth** for audio rendering

## 📧 Contact

- GitHub: [onyrix/studio_onyrix](https://github.com/onyrix/studio_onyrix)
- Issues: [Report bugs or request features](https://github.com/onyrix/studio_onyrix/issues)

---

**Studio Onyrix v2** - Hybrid AI + Rule-Based Music Generation for the Future of DAW Workflows.