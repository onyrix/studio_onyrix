import pretty_midi
import random
from utils import *
from style_engine import get_style_progression


def voice_lead(prev, next_c):
    """
    Voice leading: find the closest inversion for smooth chord transitions.
    
    Args:
        prev: Previous chord notes
        next_c: Next chord notes
    
    Returns:
        list: Voiced chord notes
    """
    if not prev:
        return next_c

    out = []
    for n in next_c:
        opts = [n-12, n, n+12]
        best = min(opts, key=lambda x: min(abs(x-p) for p in prev))
        out.append(best)
    return out


def build_complex_chord(scale, degree, complexity):
    """
    Build a chord with complexity based on the style.
    
    Args:
        scale: The scale notes
        degree: Scale degree (0-6)
        complexity: 0.0-1.0, where 0=triad, 1=extended chords
    
    Returns:
        list: Chord notes
    """
    # Basic triad
    chord = [scale[degree % 7], scale[(degree + 2) % 7], scale[(degree + 4) % 7]]
    
    if complexity < 0.3:
        # Just triads
        return chord
    
    # Add 7th
    if complexity >= 0.3:
        seventh = scale[(degree + 6) % 7]
        chord.append(seventh)
    
    # Add 9th, 11th, 13th for higher complexity
    if complexity >= 0.6:
        ninth = scale[(degree + 8) % 7] + 12  # 9th is one octave + 2
        chord.append(ninth)
    
    if complexity >= 0.8:
        # Add extensions or alterations
        if random.random() < 0.5:
            # Add 11th
            eleventh = scale[(degree + 10) % 7] + 12
            chord.append(eleventh)
        else:
            # Add 13th
            thirteenth = scale[(degree + 12) % 7] + 12
            chord.append(thirteenth)
    
    if complexity >= 0.9 and random.random() < 0.3:
        # Add alterations (b9, #9, b5, #5)
        alteration = random.choice([-1, 1])
        chord = [n + alteration if random.random() < 0.3 else n for n in chord]
    
    return chord


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
    
    # Select progression - use style-specific if available
    chaos = spec["chaos"]["level"]
    
    if typical_progressions and random.random() > chaos * 0.5:
        # Use style-typical progression
        progression_degrees = get_style_progression(
            spec["identity"].get("style", ""), 
            chaos * 0.3
        )
        if progression_degrees:
            prog = [chords[i % 7] for i in progression_degrees]
        else:
            prog = select_progression(chords, chaos)
    else:
        # Fall back to generic progression
        prog = select_progression(chords, chaos)

    prev = None

    for i in range(section["bars"]):
        # Build chord with appropriate complexity
        degree = i % len(prog)
        base_chord = prog[degree]
        
        # Apply complexity to build richer chords
        if chord_complexity > 0.3:
            chord_degree = degree % 7
            chord = build_complex_chord(scale, chord_degree, chord_complexity)
        else:
            chord = voice_lead(prev, base_chord)
        
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