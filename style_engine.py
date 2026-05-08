"""
Style Engine - Bridge module between style_library and music generation engines.

This module provides functions to:
1. Build a complete specification from a style name
2. Apply style parameters to the generation process
3. Retrieve style-specific configurations for each engine
"""

import random
from style_library import get_style, get_style_bpm, get_style_list, STYLE_LIBRARY


def build_spec_from_style(style_name, key="C_minor", chaos=0.3, custom_arrangement=None):
    """
    Build a complete generation specification from a style name.
    
    Args:
        style_name: Name of the style from STYLE_LIBRARY
        key: Musical key (e.g., "C_minor", "D_major")
        chaos: Chaos/variation level (0.0-1.0)
        custom_arrangement: Optional custom arrangement to override style template
    
    Returns:
        dict: Complete specification for generate_track()
    """
    style = get_style(style_name)
    if not style:
        raise ValueError(f"Unknown style: {style_name}. Available styles: {list(STYLE_LIBRARY.keys())}")
    
    # Determine scale type from style
    scale_type = style.get("scale_type", "natural_minor")
    # Map common scale names to our utils.py scale types
    scale_type_mapping = {
        "minor": "natural_minor",
        "major": "major",
    }
    scale_type = scale_type_mapping.get(scale_type, scale_type)
    
    # Get BPM
    bpm = get_style_bpm(style_name)
    
    # Get arrangement
    arrangement = custom_arrangement or style.get("arrangement_template", [
        {"type": "intro", "bars": 8, "intensity": 0.3},
        {"type": "verse", "bars": 16, "intensity": 0.5},
        {"type": "chorus", "bars": 16, "intensity": 0.8},
        {"type": "outro", "bars": 8, "intensity": 0.3}
    ])
    
    spec = {
        "identity": {
            "key": key,
            "scale_type": scale_type,
            "style": style_name
        },
        "time": {"bpm": bpm},
        "chaos": {"level": chaos},
        "arrangement": {
            "sections": arrangement
        },
        "style_params": {
            "drum_density": style.get("drum_density", 0.5),
            "swing": style.get("swing", 0.0),
            "chord_complexity": style.get("chord_complexity", 0.3),
            "bass_pattern": style.get("bass_pattern", "simple"),
            "melody_density": style.get("melody_density", 0.5),
            "patterns": style.get("patterns", {}),
            "typical_progressions": style.get("typical_progressions", None),
            "instruments": style.get("instruments", {})
        }
    }
    
    return spec


def get_style_progression(style_name, chaos=0.0):
    """
    Get a chord progression typical for the style.
    
    Args:
        style_name: Name of the style
        chaos: Amount of randomization (0.0-1.0)
    
    Returns:
        list: Chord progression as scale degrees
    """
    style = get_style(style_name)
    if not style or not style.get("typical_progressions"):
        return None
    
    progressions = style["typical_progressions"]
    
    if random.random() < chaos and len(progressions) > 1:
        # Add some chaos by modifying the progression
        progression = random.choice(progressions).copy()
        for i in range(len(progression)):
            if random.random() < chaos * 0.5:
                progression[i] = random.randint(0, 6)
        return progression
    
    return random.choice(progressions)


def get_style_patterns(style_name):
    """
    Get drum patterns for a style.
    
    Args:
        style_name: Name of the style
    
    Returns:
        dict: Drum patterns for kick, snare, hihat
    """
    style = get_style(style_name)
    if not style:
        return {
            "kick": [1,0,0,0,1,0,0,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [1,0]*8
        }
    return style.get("patterns", {})


def get_style_instrument(style_name, instrument_type="lead"):
    """
    Get the instrument name for a specific role in a style.
    
    Args:
        style_name: Name of the style
        instrument_type: Type of instrument ("lead", "pad", "bass")
    
    Returns:
        str: MIDI instrument name
    """
    style = get_style(style_name)
    if not style:
        instruments = {
            "lead": "Lead 1 (square)",
            "pad": "Pad 1 (new age)",
            "bass": "Electric Bass (finger)"
        }
        return instruments.get(instrument_type, "Lead 1 (square)")
    
    instruments = style.get("instruments", {})
    return instruments.get(instrument_type, "Lead 1 (square)")


def get_style_info(style_name=None):
    """
    Get information about available styles.
    
    Args:
        style_name: Optional specific style name
    
    Returns:
        dict or list: Style information or list of style names
    """
    if style_name:
        style = get_style(style_name)
        if not style:
            return None
        return {
            "name": style_name,
            "bpm_range": style["bpm_range"],
            "drum_density": style["drum_density"],
            "swing": style["swing"],
            "scale_type": style.get("scale_type", "natural_minor"),
            "chord_complexity": style.get("chord_complexity", 0.3),
            "bass_pattern": style.get("bass_pattern", "simple"),
            "melody_density": style.get("melody_density", 0.5),
            "has_patterns": bool(style.get("patterns")),
            "arrangement_sections": len(style.get("arrangement_template", []))
        }
    
    return {name: {
        "bpm_range": s["bpm_range"],
        "drum_density": s["drum_density"],
        "swing": s["swing"],
        "scale_type": s.get("scale_type", "natural_minor")
    } for name, s in STYLE_LIBRARY.items()}