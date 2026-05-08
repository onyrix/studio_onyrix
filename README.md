# Studio Onyrix

**Studio Onyrix** è un sistema di generazione musicale basato su regole algoritmiche che crea composizioni MIDI complete in diversi stili musicali. Il progetto combina motori specializzati per melodia, armonia, batteria e basso con una libreria di stili musicali dettagliata per produrre brani strutturati con arrangiamenti coerenti.

## 🎵 Caratteristiche Principali

- **Generazione multi-stile**: Supporta 25+ stili musicali (trap, lofi, techno, jazz, rock, ambient, e molti altri)
- **Architettura modulare**: Motori separati per melodia, armonia, batteria e basso
- **Memoria tematica**: Sistema di evoluzione dei motivi musicali che mantiene coerenza tematica
- **Arrangiamenti strutturati**: Genera sezioni musicali complete (intro, verse, chorus, bridge, outro)
- **Controllo della creatività**: Parametro "chaos" per regolare il livello di variazione e imprevedibilità
- **Output duplice**: Genera sia file MIDI che audio WAV

## 🏗️ Architettura del Sistema

Il progetto è organizzato in moduli specializzati:

- **`main.py`**: Punto di ingresso principale e funzioni di generazione track
- **`melody_engine.py`**: Motore per la generazione di linee melodiche
- **`harmonic_engine.py`**: Motore per la generazione di progressioni armoniche e accordi
- **`drums_bass.py`**: Motore per pattern ritmici di batteria e linee di basso
- **`style_engine.py`**: Sistema di costruzione specifiche basate sugli stili
- **`style_library.py`**: Libreria completa di 25+ stili musicali con parametri dettagliati
- **`global_memory.py`**: Sistema di memoria tematica per l'evoluzione dei motivi
- **`audio_render.py`**: Rendering audio da MIDI a WAV
- **`utils.py`**: Funzioni utility per teoria musicale e operazioni comuni
- **`automation.py`**: Sistema di automazione per parametri musicali

## 🎼 Libreria Stili Musicali

Il sistema include una vasta libreria di stili musicali organizzati per categorie:

### Hip Hop / Urban
- **Trap** (130-160 BPM) - Pattern ritmici complessi, bassi syncopated
- **Drill** (130-145 BPM) - Pattern caratteristici, bassi sliding
- **Boom Bap** (80-100 BPM) - Swing marcato, basso walking
- **Lo-fi** (65-90 BPM) - Atmosfere rilassate, accordi complessi

### Club / Electronic
- **House** (118-130 BPM) - Four-on-the-floor, struttura build/drop
- **Deep House** (118-122 BPM) - Scale doriche, basso groovy
- **Techno** (125-140 BPM) - Pattern ripetitivi, scale frigie
- **Dubstep** (135-145 BPM) - Bassi wobble, drop intensi
- **Drum & Bass** (165-180 BPM) - Pattern veloci, bassi rolling

### Cinematic / Atmos
- **Ambient** (40-80 BPM) - Atmosfere eteree, densità minima
- **Cinematic** (60-100 BPM) - Arrangiamenti orchestrali, build drammatici
- **Downtempo** (80-110 BPM) - Ritmi rilassati, armonie complesse

### Band / Acoustic
- **Rock** (90-140 BPM) - Struttura classica, chitarre elettriche
- **Funk** (95-120 BPM) - Ritmi sincopati, basso slap
- **Jazz** (90-140 BPM) - Swing, walking bass, accordi complessi

### Synth / Retro / Electronic
- **Synthpop** (100-120 BPM) - Synth melodici, struttura pop
- **Synthwave** (85-110 BPM) - Atmosfere retrò, arpeggiatori
- **Retrowave** (90-115 BPM) - Stile anni '80, driving bass
- **Outrun** (95-125 BPM) - Energetico, chitarre synth
- **Darkwave** (90-115 BPM) - Atmosfere oscure, scale frigie
- **EBM** (120-140 BPM) - Electronic Body Music, pattern marziali
- **Electro** (110-130 BPM) - Electro-funk, ritmi funky
- **IDM** (90-160 BPM) - Sperimentale, progressioni cromatiche
- **Glitch** (70-130 BPM) - Pattern irregolari, scale a toni interi
- **Electronic Pop** (100-128 BPM) - Struttura pop moderna

## 🚀 Installazione

### Prerequisiti
- Python 3.7 o superiore
- pip (Python package manager)

### Passaggi di Installazione

```bash
# Clona il repository
git clone https://github.com/onyrix/studio_onyrix.git
cd studio_onyrix

# Installa le dipendenze Python
pip install pretty_midi mido numpy

# Installa FluidSynth per il rendering audio
# Su Windows (con vcpkg o download diretto)
# Su macOS: brew install fluidsynth
# Su Linux: sudo apt-get install fluidsynth fluidsynth-dev
pip install fluidsynth
```

## 🎯 Utilizzo

### Generazione Base

```bash
# Genera un brano trap in Fa minore con caos 0.3 (default)
python main.py

# Genera un brano in uno stile specifico
python main.py lofi D_major 0.2

# Specifica stile, tonalità e livello di caos
python main.py techno C_minor 0.5
```

### Comandi Disponibili

```bash
# Lista tutti gli stili disponibili
python main.py --list
# oppure
python main.py -l
```

### Parametri della riga di comando

1. **style** (opzionale): Nome dello stile musicale (default: "trap")
2. **key** (opzionale): Tonalità nel formato "Nota_tipo" (default: "F_minor")
   - Esempi: "C_major", "D_minor", "G_major", "A_minor"
3. **chaos** (opzionale): Livello di variazione da 0.0 a 1.0 (default: 0.3)
   - 0.0 = molto prevedibile e coerente
   - 1.0 = massimamente vario e imprevedibile

### Output

Il sistema genera due file per ogni esecuzione:
- **MIDI**: `output/{style}_{key}.mid` - File MIDI modificabile in qualsiasi DAW
- **Audio**: `output/{style}_{key}.wav` - File audio renderizzato

### Esempio di Utilizzo Programmattico

```python
from main import generate_track_with_style, list_available_styles

# Lista stili disponibili
list_available_styles()

# Genera un brano jazz in Re minore
midi_track = generate_track_with_style("jazz", "D_minor", chaos=0.4)

# Salva il MIDI
midi_track.write("output/my_jazz_track.mid")

# Renderizza in audio
from audio_render import render_to_audio
render_to_audio(midi_track, "output/my_jazz_track.wav")
```

## 🧠 Sistema di Generazione

### Memoria Tematica (MotifMemory)

Il sistema utilizza una memoria tematica che evolve attraverso le sezioni del brano:
- **Tema base**: Genera un motivo iniziale di 8 note
- **Evoluzione**: Modifica il tema in base al parametro chaos e al tipo di sezione
- **Coerenza**: Mantiene relazioni tematiche tra le diverse sezioni
- **Variazione contestuale**: Le sezioni "drop" sono più stabili, le sezioni "build" più varie

### Parametri Musicali per Stile

Ogni stile nella libreria definisce:
- **BPM range**: Intervallo di tempo musicale
- **Drum density**: Densità dei pattern ritmici (0.0-1.0)
- **Swing**: Quantità di groove/shuffle
- **Pattern ritmici**: Kick, snare, hi-hat patterns
- **Scale type**: Tipo di scala (maggiore, minore, dorica, frigia, etc.)
- **Chord complexity**: Complessità armonica (0=triadi semplici, 1=accordi estesi)
- **Bass pattern**: Tipo di linea di basso (walking, syncopated, driving, etc.)
- **Melody density**: Densità melodica (0.0-1.0)
- **Progressioni tipiche**: Sequenze armoniche caratteristiche
- **Strumenti**: Lead, pad e basso tipici dello stile
- **Arrangement template**: Struttura della canzone con intensità progressive

## 📁 Struttura del Progetto

```
studio_onyrix/
├── main.py                 # Punto di ingresso principale
├── melody_engine.py        # Motore generazione melodia
├── harmonic_engine.py      # Motore generazione armonia
├── drums_bass.py           # Motore generazione batteria e basso
├── style_engine.py         # Motore di costruzione stili
├── style_library.py        # Libreria degli stili musicali
├── global_memory.py        # Sistema di memoria tematica
├── audio_render.py         # Rendering audio
├── automation.py           # Sistema di automazione
├── utils.py                # Funzioni utility
├── README.md               # Questa documentazione
├── docs/
│   └── install_and_run.txt # Istruzioni di installazione
└── output/                 # Directory output (MIDI e WAV)
    ├── jazz_G_major.mid
    ├── jazz_G_major.wav
    ├── lofi_D_major.mid
    ├── lofi_D_major.wav
    ├── techno_F_minor.mid
    ├── techno_F_minor.wav
    ├── trap_C_minor.mid
    └── trap_C_minor.wav
```

## 🔧 Sviluppo

### Aggiungere un Nuovo Stile

Per aggiungere un nuovo stile musicale, modifica `style_library.py`:

```python
"nuovo_stile": {
    "bpm_range": (100, 120),
    "drum_density": 0.5,
    "swing": 0.1,
    "patterns": {
        "kick": [1,0,0,0,1,0,0,0],
        "snare": [0,0,1,0,0,0,1,0],
        "hihat": [1,0]*8
    },
    "scale_type": "minor",
    "chord_complexity": 0.4,
    "bass_pattern": "simple",
    "melody_density": 0.5,
    "typical_progressions": [[0, 3, 4], [0, 4, 3]],
    "instruments": {
        "lead": "Synth Lead",
        "pad": "Pad 1 (new age)",
        "bass": "Synth Bass 1"
    },
    "arrangement_template": [
        {"type": "intro", "bars": 4, "intensity": 0.2},
        {"type": "verse", "bars": 8, "intensity": 0.5},
        {"type": "chorus", "bars": 8, "intensity": 0.8},
        {"type": "outro", "bars": 4, "intensity": 0.3}
    ]
}
```

### Tipi di Sezione Supportati

- `intro` - Introduzione
- `verse` - Strofa
- `chorus` - Ritornello
- `bridge` - Ponte
- `solo` - Assolo
- `build` - Costruzione (tipico electronic)
- `drop` - Drop (tipico electronic)
- `break` - Pausa/breakdown
- `pre_chorus` - Pre-ritornello
- `outro` - Conclusione

## 📝 Note Tecniche

### Dipendenze Principali
- **pretty_midi**: Libreria per la manipolazione di file MIDI
- **mido**: Additional MIDI utilities
- **numpy**: Calcoli numerici per algoritmi musicali
- **fluidsynth**: Sintetizzatore per rendering audio

### Teoria Musicale Implementata
- Scale maggiori e minori (naturale, armonica, melodica)
- Modi greci (dorico, frigio, lidio, misolidio, locrio)
- Scale speciali (cromatica, a toni interi)
- Progressioni armoniche per stile
- Teoria degli accordi e estensioni

## 🤝 Contributi

I contributi sono benvenuti! Per favore:
1. Fork del repository
2. Crea un branch per la tua feature
3. Commit delle modifiche
4. Push sul branch
5. Pull Request

## 📄 License

Questo progetto è open source e disponibile per uso personale e commerciale.

## 🙏 Ringraziamenti

- La comunità open source per le librerie musicali Python
- I musicisti e produttori che hanno ispirato i parametri degli stili
- Il progetto FluidSynth per il rendering audio di qualità

## 📧 Contatti

Per domande, suggerimenti o collaborazioni:
- GitHub: [onyrix/studio_onyrix](https://github.com/onyrix/studio_onyrix)

---

**Studio Onyrix** - Generazione musicale algoritmica per creatori di musica digitale.