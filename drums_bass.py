import random
import pretty_midi

from style_engine import get_style_patterns


def generate_drums(pm, spec, section, t0):
    """
    Generate drum patterns based on style parameters.
    
    Args:
        pm: PrettyMIDI object
        spec: Full specification including style_params
        section: Section definition (type, bars, intensity)
        t0: Start time in seconds
    
    Returns:
        tuple: (end_time, kick_times)
    """
    inst = pretty_midi.Instrument(program=0, is_drum=True)

    bpm = spec["time"]["bpm"]
    step = 60 / bpm / 4
    steps = section["bars"] * 16
    
    # Get style parameters
    style_params = spec.get("style_params", {})
    drum_density = style_params.get("drum_density", 0.7)
    swing = style_params.get("swing", 0.0)
    patterns = style_params.get("patterns", {})
    
    # Get intensity from section
    intensity = section.get("intensity", 0.5)
    
    # Apply intensity to density (higher intensity = more drums)
    effective_density = min(1.0, drum_density * (0.5 + intensity * 0.5))

    kicks = []
    
    # Get patterns or use defaults
    kick_pattern = patterns.get("kick", [1,0,0,0,1,0,0,0])
    snare_pattern = patterns.get("snare", [0,0,1,0,0,0,1,0])
    hihat_pattern = patterns.get("hihat", [1,0]*8)
    
    # Extend patterns to 16 steps if needed
    def extend_pattern(pattern, length=16):
        if not pattern:
            return [0] * length
        while len(pattern) < length:
            pattern = pattern + pattern
        return pattern[:length]
    
    kick_pattern = extend_pattern(kick_pattern)
    snare_pattern = extend_pattern(snare_pattern)
    hihat_pattern = extend_pattern(hihat_pattern)

    for i in range(steps):
        # Apply swing to timing
        swing_offset = 0
        if swing > 0 and i % 2 == 1:  # Apply swing to off-beats
            swing_offset = swing * step * 0.5
        
        t = t0 + i * step + swing_offset

        # Pattern index (8-step patterns repeated)
        pattern_idx = i % 8

        # Kick drum - use pattern with density variation
        if kick_pattern[pattern_idx] == 1:
            if random.random() < effective_density:
                inst.notes.append(pretty_midi.Note(100, 36, t, t + 0.1))
                kicks.append(t)
        elif random.random() < 0.05 * effective_density:
            # Occasional extra kicks for variation
            inst.notes.append(pretty_midi.Note(100, 36, t, t + 0.1))
            kicks.append(t)

        # Snare drum - use pattern
        if snare_pattern[pattern_idx] == 1:
            if random.random() < effective_density:
                inst.notes.append(pretty_midi.Note(100, 38, t, t + 0.1))
        elif random.random() < 0.03 * effective_density:
            # Occasional ghost notes
            inst.notes.append(pretty_midi.Note(60, 38, t, t + 0.05))

        # Hi-hat - use pattern with density
        if hihat_pattern[i % 16] == 1:
            if random.random() < effective_density:
                velocity = 60 + int(40 * effective_density)
                inst.notes.append(pretty_midi.Note(velocity, 42, t, t + 0.05))
        elif random.random() < 0.3 * effective_density:
            # Some variation
            inst.notes.append(pretty_midi.Note(50, 42, t, t + 0.05))

    pm.instruments.append(inst)
    return t0 + steps * step, kicks


def generate_bass(pm, spec, section, t0, kicks):
    """
    Generate bass lines based on style parameters.
    
    Args:
        pm: PrettyMIDI object
        spec: Full specification including style_params
        section: Section definition (type, bars, intensity)
        t0: Start time in seconds
        kicks: List of kick drum times
    """
    style_params = spec.get("style_params", {})
    bass_pattern_type = style_params.get("bass_pattern", "simple")
    intensity = section.get("intensity", 0.5)
    
    # Select bass instrument based on style
    bass_instrument = style_params.get("instruments", {}).get("bass", "Electric Bass (finger)")
    try:
        program = pretty_midi.instrument_name_to_program(bass_instrument)
    except:
        program = 33  # Electric Bass (finger) default
    
    inst = pretty_midi.Instrument(program=program)

    bpm = spec["time"]["bpm"]
    step = 60 / bpm / 4
    
    # Get the root note from the key
    key = spec["identity"]["key"]
    # Map note names to MIDI (octave 2 for bass)
    note_map = {"C": 48, "D": 50, "E": 52, "F": 53, "G": 55, "A": 57, "B": 59}
    root_midi = note_map.get(key.split("_")[0], 48)  # C2 = 48
    
    # Bass pattern behaviors
    bass_density = style_params.get("drum_density", 0.5)  # Use drum density as proxy
    
    for k in kicks:
        # Different patterns based on style
        if bass_pattern_type == "simple":
            # Simple: play on kick with occasional variations
            if random.random() < 0.8 * intensity:
                inst.notes.append(pretty_midi.Note(
                    90,
                    root_midi,
                    k,
                    k + step * random.choice([1, 2])
                ))
        
        elif bass_pattern_type == "syncopated":
            # Syncopated: play on and off beats
            if random.random() < 0.7:
                duration = step * random.choice([1, 2, 3])
                inst.notes.append(pretty_midi.Note(
                    90,
                    root_midi,
                    k,
                    k + duration
                ))
                # Add syncopated note
                if random.random() < 0.4:
                    inst.notes.append(pretty_midi.Note(
                        80,
                        root_midi + random.choice([0, 5, 7, 12]),
                        k + step * 2,
                        k + step * 3
                    ))
        
        elif bass_pattern_type == "driving":
            # Driving: steady eighth notes
            for offset in range(0, 4):
                if random.random() < 0.6 * intensity:
                    inst.notes.append(pretty_midi.Note(
                        90,
                        root_midi,
                        k + offset * step,
                        k + (offset + 1) * step
                    ))
        
        elif bass_pattern_type == "walking":
            # Walking: quarter notes moving through scale
            if random.random() < 0.9:
                inst.notes.append(pretty_midi.Note(
                    90,
                    root_midi + random.choice([0, 2, 4, 5, 7]),
                    k,
                    k + step * 2
                ))
        
        elif bass_pattern_type == "arpeggiated":
            # Arpeggiated: broken chord pattern
            arp_notes = [root_midi, root_midi + 7, root_midi + 12, root_midi + 7]
            for i, note in enumerate(arp_notes):
                if random.random() < 0.7:
                    inst.notes.append(pretty_midi.Note(
                        85,
                        note,
                        k + i * step,
                        k + (i + 1) * step
                    ))
        
        elif bass_pattern_type == "four_on_floor":
            # Four on the floor: steady quarter notes
            for offset in range(0, 4):
                inst.notes.append(pretty_midi.Note(
                    90,
                    root_midi,
                    k + offset * step,
                    k + (offset + 1) * step
                ))
        
        elif bass_pattern_type == "wobble":
            # Wobble: LFO-like effect with pitch variation
            if random.random() < 0.8:
                base_note = root_midi
                wobble = random.choice([0, 0, 1, -1])  # Subtle pitch wobble
                inst.notes.append(pretty_midi.Note(
                    95,
                    base_note + wobble,
                    k,
                    k + step * 2
                ))
        
        elif bass_pattern_type == "rolling":
            # Rolling DnB style: fast pattern
            for offset in [0, 1.5, 3]:
                if random.random() < 0.6:
                    inst.notes.append(pretty_midi.Note(
                        90,
                        root_midi + random.choice([0, 5, 7]),
                        k + offset * step,
                        k + (offset + 1) * step
                    ))
        
        elif bass_pattern_type == "sliding":
            # Drill/Trap sliding bass
            if random.random() < 0.85:
                slide_note = root_midi + random.choice([0, -5, -7, 12])
                inst.notes.append(pretty_midi.Note(
                    95,
                    slide_note,
                    k,
                    k + step * random.choice([2, 3, 4])
                ))
        
        elif bass_pattern_type == "groovy":
            # Groovy: syncopated with ghost notes
            if random.random() < 0.75:
                inst.notes.append(pretty_midi.Note(
                    85,
                    root_midi,
                    k,
                    k + step * 1.5
                ))
                if random.random() < 0.3:
                    inst.notes.append(pretty_midi.Note(
                        60,
                        root_midi + 7,
                        k + step * 2,
                        k + step * 2.5
                    ))
        
        elif bass_pattern_type == "funky":
            # Funky: syncopated with octaves
            if random.random() < 0.8:
                inst.notes.append(pretty_midi.Note(
                    90,
                    root_midi,
                    k,
                    k + step * 1.5
                ))
                if random.random() < 0.5:
                    inst.notes.append(pretty_midi.Note(
                        70,
                        root_midi + 12,
                        k + step * 2,
                        k + step * 3
                    ))
        
        elif bass_pattern_type == "slap":
            # Slap bass: percussive with pops
            if random.random() < 0.7:
                inst.notes.append(pretty_midi.Note(
                    100,
                    root_midi,
                    k,
                    k + step * 0.5
                ))
                if random.random() < 0.6:
                    inst.notes.append(pretty_midi.Note(
                        80,
                        root_midi + random.choice([7, 12]),
                        k + step * 1,
                        k + step * 1.5
                    ))
        
        elif bass_pattern_type == "drone":
            # Drone: long sustained notes
            if random.random() < 0.5:
                inst.notes.append(pretty_midi.Note(
                    70,
                    root_midi,
                    k,
                    k + step * 8  # Long drone
                ))
        
        elif bass_pattern_type == "orchestral":
            # Orchestral: sustained bass notes
            if random.random() < 0.6:
                inst.notes.append(pretty_midi.Note(
                    80,
                    root_midi,
                    k,
                    k + step * 4
                ))
        
        elif bass_pattern_type == "minimal":
            # Minimal: sparse bass
            if random.random() < 0.3 * intensity:
                inst.notes.append(pretty_midi.Note(
                    85,
                    root_midi,
                    k,
                    k + step * 4
                ))
        
        elif bass_pattern_type == "experimental" or bass_pattern_type == "glitchy":
            # Experimental/Glitch: unpredictable patterns
            if random.random() < 0.5:
                note = root_midi + random.choice([-12, -7, -5, 0, 5, 7, 12])
                duration = step * random.choice([0.5, 1, 1.5, 2, 3])
                inst.notes.append(pretty_midi.Note(
                    random.randint(60, 100),
                    note,
                    k,
                    k + duration
                ))
        
        else:
            # Default fallback
            if random.random() < 0.8:
                inst.notes.append(pretty_midi.Note(
                    90,
                    root_midi,
                    k,
                    k + step * random.choice([1, 2])
                ))

    pm.instruments.append(inst)