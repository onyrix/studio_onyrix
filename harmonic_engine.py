import pretty_midi
import random
from utils import *
from style_engine import get_style_progression
from harmony_engine import (
    get_chord_for_degree, 
    get_functional_progression,
    voice_lead_satb,
    position_chord_satb,
    STANDARD_VOICE_RANGES,
    INSTRUMENT_VOICE_RANGES
)


def voice_lead(prev, next_c):
    """
    Voice leading: find the closest inversion for smooth chord transitions.
    Uses the advanced SATB voice leading from harmony_engine.
    
    Args:
        prev: Previous chord notes
        next_c: Next chord notes
    
    Returns:
        list: Voiced chord notes
    """
    if not prev:
        return position_chord_satb(next_c, INSTRUMENT_VOICE_RANGES)
    
    return voice_lead_satb(prev, next_c, INSTRUMENT_VOICE_RANGES)


def build_complex_chord(scale_name, degree, complexity):
    """
    Build a chord with correct quality and complexity based on the style.
    Uses the advanced harmony engine for proper chord construction.
    
    Args:
        scale_name: Name of the scale (e.g., "C_major")
        degree: Scale degree (0-6)
        complexity: 0.0-1.0, where 0=triad, 1=extended chords
    
    Returns:
        list: Chord notes with correct quality
    """
    # Use the advanced harmony engine for proper chord construction
    return get_chord_for_degree(scale_name, degree, complexity, octave=4)


def generate_chords(pm, spec, section, t0):
    """
    Generate chord progressions based on style parameters.
    
    Args:
        pm: PrettyMIDI object
        spec: Full specification including style_params
        section: Section definition (type, bars, intensity)
        t0: Start time in seconds
    """
    style_params = spec.get("style_params", {})
    chord_complexity = style_params.get("chord_complexity", 0.3)
    typical_progressions = style_params.get("typical_progressions", None)
    
    # Select instrument based on style
    pad_instrument = style_params.get("instruments", {}).get("pad", "Synth Strings 1")
    try:
        program = pretty_midi.instrument_name_to_program(pad_instrument)
    except:
        program = 50  # Synth Strings 1 default
    
    inst = pretty_midi.Instrument(program=program)

    bpm = spec["time"]["bpm"]
    bar = 60 / bpm * 4
    
    # Get section intensity for velocity/density control
    intensity = section.get("intensity", 0.5)

    scale = get_scale_notes(
        spec["identity"]["key"],
        spec["identity"].get("scale_type", "natural_minor")
    )

    chords = build_chords(scale)
    
    # Select progression - use style-specific functional progressions
    chaos = spec["chaos"]["level"]
    style_name = spec["identity"].get("style", "")
    
    if typical_progressions and random.random() > chaos * 0.5:
        # Use style-typical functional progression
        progression_degrees = get_functional_progression(style_name, section["bars"])
        # Build chords with correct quality
        prog = []
        for degree in progression_degrees:
            chord = get_chord_for_degree(
                spec["identity"]["key"], 
                degree, 
                chord_complexity
            )
            prog.append(chord)
    elif typical_progressions:
        progression_degrees = get_style_progression(
            spec["identity"].get("style", ""), 
            chaos * 0.3
        )
        if progression_degrees:
            prog = []
            for degree in progression_degrees:
                chord = get_chord_for_degree(
                    spec["identity"]["key"],
                    degree,
                    chord_complexity
                )
                prog.append(chord)
        else:
            prog = select_progression(chords, chaos)
    else:
        # Fall back to generic progression
        prog = select_progression(chords, chaos)

    prev = None

    for i in range(section["bars"]):
        # Get chord for this bar
        degree = i % len(prog)
        base_chord = prog[degree]
        
        # Apply voice leading for smooth transitions
        if prev:
            chord = voice_lead(prev, base_chord)
        else:
            chord = position_chord_satb(base_chord, INSTRUMENT_VOICE_RANGES)
        
        t = t0 + i * bar
        
        # Adjust velocity based on intensity
        velocity = 60 + int(40 * intensity)
        
        # Arpeggiate chords for higher complexity styles
        if chord_complexity > 0.5 and random.random() < 0.3:
            # Arpeggiated chords
            for j, n in enumerate(chord):
                note_time = t + j * (bar / len(chord))
                inst.notes.append(pretty_midi.Note(
                    velocity,
                    n,
                    note_time,
                    note_time + bar / len(chord) * 0.8
                ))
        else:
            # Block chords
            for n in chord:
                inst.notes.append(pretty_midi.Note(
                    velocity,
                    n,
                    t,
                    t + bar
                ))

        prev = chord

    pm.instruments.append(inst)


def generate_ambient_pads(pm, spec, section, t0):
    """
    Generate ambient pad layers for atmospheric styles.
    
    Args:
        pm: PrettyMIDI object
        spec: Full specification
        section: Section definition
        t0: Start time
    """
    style_params = spec.get("style_params", {})
    chord_complexity = style_params.get("chord_complexity", 0.5)
    intensity = section.get("intensity", 0.5)
    
    # Use pad instrument
    pad_instrument = style_params.get("instruments", {}).get("pad", "Pad 1 (new age)")
    try:
        program = pretty_midi.instrument_name_to_program(pad_instrument)
    except:
        program = 88  # Pad 1 (new age) default
    
    inst = pretty_midi.Instrument(program=program)
    
    bpm = spec["time"]["bpm"]
    bar = 60 / bpm * 4
    
    scale = get_scale_notes(
        spec["identity"]["key"],
        spec["identity"].get("scale_type", "natural_minor")
    )
    
    # Long, sustained chords
    chords_to_play = []
    for i in range(0, section["bars"], 2):  # Change chord every 2 bars
        degree = i % 7
        chord = build_complex_chord(scale, degree, min(chord_complexity, 0.7))
        chords_to_play.append((i, chord))
    
    for bar_idx, chord in chords_to_play:
        t = t0 + bar_idx * bar
        velocity = 40 + int(30 * intensity)
        
        for n in chord:
            inst.notes.append(pretty_midi.Note(
                velocity,
                n,
                t,
                t + bar * 2  # Long sustained notes
            ))
    
    pm.instruments.append(inst)