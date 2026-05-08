import random
import pretty_midi
from utils import *
from style_engine import get_style_instrument


def rhythm_gate(t, kicks, melody_density=0.5):
    """
    Determine if a note should be played at this time based on rhythm and density.
    
    Args:
        t: Current time
        kicks: List of kick drum times for rhythmic alignment
        melody_density: 0.0-1.0, higher = more notes
    
    Returns:
        bool: Whether to play a note
    """
    # Check if near a kick (more likely to play)
    for k in kicks:
        if abs(k - t) < 0.05:
            return True
    
    # Base probability adjusted by density
    return random.random() < melody_density * 0.4


def generate_melody_rhythm(melody_density, bpm):
    """
    Generate a rhythmic pattern based on melody density.
    
    Args:
        melody_density: 0.0-1.0
        bpm: Beats per minute
    
    Returns:
        list: List of note durations in beats
    """
    step = 60 / bpm / 4  # 16th note
    
    if melody_density < 0.3:
        # Sparse: mostly quarter and half notes
        return [step * 4, step * 8]
    elif melody_density < 0.5:
        # Moderate: eighth and quarter notes
        return [step * 2, step * 4]
    elif melody_density < 0.7:
        # Dense: sixteenth and eighth notes
        return [step, step * 2, step * 4]
    else:
        # Very dense: fast runs with varied durations
        return [step, step * 1.5, step * 2, step * 3]


def generate_melody(pm, spec, section, t0, kicks, motif):
    """
    Generate melody lines based on style parameters.
    
    Args:
        pm: PrettyMIDI object
        spec: Full specification including style_params
        section: Section definition (type, bars, intensity)
        t0: Start time in seconds
        kicks: List of kick drum times
        motif: Current motif from memory
    """
    style_params = spec.get("style_params", {})
    melody_density = style_params.get("melody_density", 0.5)
    
    # Select instruments based on style
    lead_instrument = style_params.get("instruments", {}).get("lead", "Lead 1 (square)")
    counter_instrument = style_params.get("instruments", {}).get("pad", "Pad 1 (new age)")
    
    try:
        lead_program = pretty_midi.instrument_name_to_program(lead_instrument)
    except:
        lead_program = 80  # Lead 1 (square) default
    
    try:
        counter_program = pretty_midi.instrument_name_to_program(counter_instrument)
    except:
        counter_program = 88  # Pad 1 (new age) default
    
    lead = pretty_midi.Instrument(program=lead_program)
    counter = pretty_midi.Instrument(program=counter_program)

    bpm = spec["time"]["bpm"]
    step = 60 / bpm / 4
    steps = section["bars"] * 16
    
    # Get section intensity
    intensity = section.get("intensity", 0.5)
    
    # Adjust melody density by intensity (more intense = more notes)
    effective_density = melody_density * (0.5 + intensity * 0.5)

    scale = get_scale_notes(spec["identity"]["key"])
    
    # Get available note durations based on density
    note_durations = generate_melody_rhythm(effective_density, bpm)

    i = 0
    while i < steps:
        t = t0 + i * step
        
        # Use rhythm gate with effective density
        if not rhythm_gate(t, kicks, effective_density):
            i += 1
            continue
        
        # Select note from motif
        note = motif[i % len(motif)]
        
        # Apply tension/modification by section type
        if section["type"] == "build":
            # Build tension with ascending notes
            note += random.choice([0, 12, 7])
        elif section["type"] == "drop":
            # Stable, powerful notes
            note = note
        elif section["type"] == "intro" or section["type"] == "outro":
            # Softer, lower notes
            note = note - random.choice([0, 12])
        elif section["type"] == "verse":
            # Moderate range
            note += random.choice([0, 7])
        elif section["type"] == "chorus":
            # Higher, more prominent
            note += random.choice([0, 12])
        elif section["type"] == "solo":
            # Wide range, expressive
            note += random.choice([-12, 0, 12, 24])
        elif section["type"] == "bridge":
            # Contrasting
            note += random.choice([0, 5, 7])
        
        # Select duration
        duration = random.choice(note_durations)
        
        # Velocity based on intensity
        velocity = 70 + int(30 * intensity)
        
        # Lead note
        lead.notes.append(pretty_midi.Note(
            velocity,
            note + 12,  # Play an octave higher for lead
            t,
            t + duration
        ))
        
        # Counter melody - less frequent, harmonizing
        if random.random() < 0.3 * effective_density:
            # Harmony interval based on style
            harmony_interval = random.choice([-7, -5, -3, 3, 5, 7])
            counter_note = note + harmony_interval
            
            counter.notes.append(pretty_midi.Note(
                60,
                counter_note,
                t + step * 0.5,  # Slightly offset
                t + duration * 1.5
            ))
        
        # Advance by duration (in steps)
        i += max(1, int(duration / step))
    
    pm.instruments.append(lead)
    pm.instruments.append(counter)


def generate_lead_melody(pm, spec, section, t0, kicks, motif):
    """
    Generate a more prominent lead melody for featured sections.
    
    Args:
        pm: PrettyMIDI object
        spec: Full specification
        section: Section definition
        t0: Start time
        kicks: List of kick times
        motif: Current motif
    """
    style_params = spec.get("style_params", {})
    melody_density = style_params.get("melody_density", 0.5)
    intensity = section.get("intensity", 0.5)
    
    lead_instrument = style_params.get("instruments", {}).get("lead", "Lead 1 (square)")
    try:
        program = pretty_midi.instrument_name_to_program(lead_instrument)
    except:
        program = 80
    
    inst = pretty_midi.Instrument(program=program)
    
    bpm = spec["time"]["bpm"]
    step = 60 / bpm / 4
    steps = section["bars"] * 16
    
    scale = get_scale_notes(spec["identity"]["key"])
    
    # More prominent melody with higher density
    effective_density = melody_density * intensity
    
    for i in range(steps):
        t = t0 + i * step
        
        if not rhythm_gate(t, kicks, effective_density * 1.5):
            continue
        
        # Use motif with more variation
        note = motif[i % len(motif)]
        
        # More variation for lead
        variation = random.choice([-12, -7, -5, 0, 5, 7, 12])
        note += variation
        
        # Tension by section
        if section["type"] in ["drop", "chorus", "solo"]:
            note += 12  # Higher for climactic sections
        
        velocity = 80 + int(20 * intensity)
        duration = step * random.choice([1, 2, 3])
        
        inst.notes.append(pretty_midi.Note(
            velocity,
            note + 12,
            t,
            t + duration
        ))
    
    pm.instruments.append(inst)


def generate_arpeggio(pm, spec, section, t0):
    """
    Generate arpeggiated patterns for electronic styles.
    
    Args:
        pm: PrettyMIDI object
        spec: Full specification
        section: Section definition
        t0: Start time
    """
    style_params = spec.get("style_params", {})
    melody_density = style_params.get("melody_density", 0.5)
    intensity = section.get("intensity", 0.5)
    
    lead_instrument = style_params.get("instruments", {}).get("lead", "Lead 1 (square)")
    try:
        program = pretty_midi.instrument_name_to_program(lead_instrument)
    except:
        program = 80
    
    inst = pretty_midi.Instrument(program=program)
    
    bpm = spec["time"]["bpm"]
    bar = 60 / bpm * 4
    step = 60 / bpm / 4
    
    scale = get_scale_notes(spec["identity"]["key"])
    chords = build_chords(scale)
    
    # Arpeggio patterns
    arp_patterns = [
        [0, 1, 2, 3],      # Up
        [3, 2, 1, 0],      # Down
        [0, 2, 1, 3],      # Up-down
        [0, 3, 1, 2],      # Random-ish
    ]
    
    pattern = random.choice(arp_patterns)
    
    for bar_idx in range(section["bars"]):
        chord_idx = bar_idx % len(chords)
        chord = chords[chord_idx]
        
        # Arpeggiate through the bar
        notes_per_bar = int(16 * melody_density)
        step_duration = (bar / notes_per_bar)
        
        for i in range(notes_per_bar):
            t = t0 + bar_idx * bar + i * step_duration
            chord_note_idx = pattern[i % len(pattern)]
            note = chord[chord_note_idx]
            
            # Add octave displacement for variety
            if i >= len(pattern):
                note += 12
            
            velocity = 60 + int(30 * intensity)
            
            inst.notes.append(pretty_midi.Note(
                velocity,
                note,
                t,
                t + step_duration * 0.8
            ))
    
    pm.instruments.append(inst)