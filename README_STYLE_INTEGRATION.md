# Style-Based Music Generation System

## Overview

This system integrates a comprehensive style library into the music generation pipeline, allowing you to generate music in 26 different styles with authentic characteristics for each genre.

## Quick Start

### Generate a track in a specific style

```bash
python main.py <style> <key> <chaos_level>
```

**Examples:**
```bash
# Generate a trap track in C minor with low chaos
python main.py trap C_minor 0.2

# Generate a lofi track in D major with medium chaos
python main.py lofi D_major 0.3

# Generate a techno track in F minor with very low chaos
python main.py techno F_minor 0.1

# Generate a jazz track in G major with high chaos
python main.py jazz G_major 0.5
```

### List all available styles

```bash
python main.py --list
```

## Available Styles (26 total)

### Hip Hop / Urban
- **trap** - BPM: 130-160, harmonic minor, syncopated bass
- **drill** - BPM: 130-145, harmonic minor, sliding bass
- **boom_bap** - BPM: 80-100, natural minor, walking bass
- **lofi** - BPM: 65-90, major key, simple bass, complex chords

### Club / Electronic
- **house** - BPM: 118-130, minor key, four-on-floor bass
- **deep_house** - BPM: 118-122, dorian mode, groovy bass
- **techno** - BPM: 125-140, phrygian mode, driving bass
- **minimal_techno** - BPM: 120-128, locrian mode, minimal bass
- **dubstep** - BPM: 135-145, harmonic minor, wobble bass
- **dnb** - BPM: 165-180, natural minor, rolling bass

### Cinematic / Atmospheric
- **ambient** - BPM: 40-80, major key, drone bass, very sparse
- **cinematic** - BPM: 60-100, harmonic minor, orchestral bass
- **downtempo** - BPM: 80-110, dorian mode, groovy bass

### Band / Acoustic
- **rock** - BPM: 90-140, major key, driving bass
- **funk** - BPM: 95-120, mixolydian mode, slap bass
- **jazz** - BPM: 90-140, dorian mode, walking bass, complex chords

### Synth / Retro / Electronic
- **synthpop** - BPM: 100-120, major key, arpeggiated bass
- **synthwave** - BPM: 85-110, natural minor, arpeggiated bass
- **retrowave** - BPM: 90-115, natural minor, driving bass
- **outrun** - BPM: 95-125, harmonic minor, driving bass
- **darkwave** - BPM: 90-115, phrygian mode, driving bass
- **ebm** - BPM: 120-140, phrygian mode, driving bass
- **electro** - BPM: 110-130, mixolydian mode, funky bass
- **idm** - BPM: 90-160, chromatic scale, experimental bass
- **glitch** - BPM: 70-130, whole tone scale, glitchy bass
- **electronic_pop** - BPM: 100-128, major key, simple bass

## Programmatic Usage

### Generate a track with style in Python

```python
from main import generate_track_with_style
from audio_render import render_to_audio

# Generate a trap track
pm = generate_track_with_style("trap", key="C_minor", chaos=0.3)

# Save MIDI
pm.write("output/my_trap_track.mid")

# Render to audio
render_to_audio(pm, "output/my_trap_track.wav")
```

### Use style_engine directly

```python
from style_engine import build_spec_from_style, get_style_info

# Build a specification from a style
spec = build_spec_from_style("lofi", key="D_major", chaos=0.2)

# Get information about a style
info = get_style_info("techno")
print(info)
# Output: {'name': 'techno', 'bpm_range': (125, 140), 'drum_density': 0.9, ...}

# Get all style information
all_styles = get_style_info()
```

## Style Parameters

Each style is defined by a comprehensive set of parameters:

### Rhythmic Parameters
- **bpm_range**: (min, max) BPM range for the style
- **drum_density**: 0.0-1.0, how dense the drum patterns are
- **swing**: 0.0-1.0, amount of swing/groove applied
- **patterns**: Kick, snare, and hi-hat patterns

### Musical Parameters
- **scale_type**: Preferred scale (major, natural_minor, harmonic_minor, dorian, phrygian, etc.)
- **chord_complexity**: 0.0-1.0, simplicity vs complexity of chords (triads vs extended chords)
- **bass_pattern**: Type of bass pattern (simple, syncopated, driving, walking, arpeggiated, etc.)
- **melody_density**: 0.0-1.0, how many melody notes are played
- **typical_progressions**: Chord progressions typical for the style

### Instrumentation
- **instruments**: Dictionary specifying lead, pad, and bass instruments

### Arrangement
- **arrangement_template**: Default song structure with section types, bar counts, and intensity levels

## How Style Integration Works

### 1. Style Library (`style_library.py`)
Contains definitions for all 26 styles with their characteristic parameters.

### 2. Style Engine (`style_engine.py`)
Bridge module that:
- Builds complete specifications from style names
- Provides style-specific progressions, patterns, and instruments
- Maps style parameters to generation engines

### 3. Updated Generation Engines

#### Drums & Bass (`drums_bass.py`)
- Uses style-specific drum patterns instead of hardcoded patterns
- Applies correct swing timing
- Adjusts density based on style and section intensity
- Generates bass lines appropriate for each style's pattern type

#### Harmony (`harmonic_engine.py`)
- Uses style-typical chord progressions
- Builds chords with appropriate complexity (triads, 7ths, 9ths, etc.)
- Selects instruments based on style
- Applies arpeggiation for complex styles

#### Melody (`melody_engine.py`)
- Adjusts note density based on style
- Uses style-appropriate instruments
- Adapts rhythmic patterns to style density
- Modifies melodic behavior based on section type

## Customization

### Override arrangement

```python
from style_engine import build_spec_from_style

# Use a custom arrangement instead of the style template
custom_arrangement = [
    {"type": "intro", "bars": 4, "intensity": 0.2},
    {"type": "verse", "bars": 8, "intensity": 0.5},
    {"type": "chorus", "bars": 8, "intensity": 0.9},
    {"type": "outro", "bars": 4, "intensity": 0.3}
]

spec = build_spec_from_style(
    "trap", 
    key="C_minor", 
    chaos=0.3,
    custom_arrangement=custom_arrangement
)
```

### Create your own style

Add a new entry to `STYLE_LIBRARY` in `style_library.py`:

```python
"my_custom_style": {
    "bpm_range": (120, 130),
    "drum_density": 0.7,
    "swing": 0.1,
    "patterns": {
        "kick": [1,0,0,0,1,0,0,0],
        "snare": [0,0,1,0,0,0,1,0],
        "hihat": [1,0]*8
    },
    "scale_type": "natural_minor",
    "chord_complexity": 0.4,
    "bass_pattern": "driving",
    "melody_density": 0.5,
    "typical_progressions": [[0, 3, 4], [0, 5, 3]],
    "instruments": {
        "lead": "Lead 1 (square)",
        "pad": "Pad 1 (new age)",
        "bass": "Electric Bass (finger)"
    },
    "arrangement_template": [
        {"type": "intro", "bars": 8, "intensity": 0.3},
        {"type": "verse", "bars": 16, "intensity": 0.5},
        {"type": "chorus", "bars": 16, "intensity": 0.8},
        {"type": "outro", "bars": 8, "intensity": 0.3}
    ]
}
```

## Technical Details

### Backward Compatibility
The system maintains full backward compatibility. You can still use the original `generate_track(spec)` function with manually crafted specifications.

### Section Types
The system recognizes various section types:
- **intro** - Opening section, usually lower intensity
- **verse** - Main narrative section
- **chorus** - Climactic, high-intensity section
- **bridge** - Contrasting middle section
- **build** - Tension-building section (electronic music)
- **drop** - Peak energy section (electronic music)
- **break** - Breakdown section
- **solo** - Featured instrumental section
- **outro** - Closing section

### Intensity System
Each section has an intensity value (0.0-1.0) that affects:
- Drum density and velocity
- Melody density and range
- Chord velocity and complexity
- Bass activity level

### Chaos Parameter
The chaos parameter (0.0-1.0) controls:
- Variation from typical progressions
- Motif evolution and variation
- Randomness in note selection
- Unpredictability in rhythms

## Examples

### Generate multiple style demos

```python
from main import generate_track_with_style
from audio_render import render_to_audio

styles = ["trap", "lofi", "techno", "jazz", "synthwave"]

for style in styles:
    print(f"Generating {style}...")
    pm = generate_track_with_style(style, "C_minor", 0.2)
    pm.write(f"output/{style}_demo.mid")
    render_to_audio(pm, f"output/{style}_demo.wav")
    print(f"  -> {style}_demo.mid / .wav")
```

### Compare same style with different chaos levels

```python
for chaos in [0.1, 0.3, 0.5, 0.8]:
    pm = generate_track_with_style("trap", "C_minor", chaos)
    pm.write(f"output/trap_chaos_{chaos}.mid")
```

## Future Enhancements

Potential improvements:
1. More detailed style parameters (articulation, dynamics)
2. Style-specific melody generation algorithms
3. Cross-style fusion capabilities
4. Machine learning-based style analysis
5. User-defined style templates
6. Style transition smoothing

## Credits

This integration maintains the original architecture while adding comprehensive style-based generation capabilities. All 26 styles are carefully crafted with authentic musical characteristics.