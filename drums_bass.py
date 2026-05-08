"""
Enhanced Drums & Bass Generator

This module provides sophisticated drum and bass generation with:
- Style-specific drum patterns with variations and fills
- Humanization (timing/velocity jitter, swing)
- Music theory-aware bass lines that follow chord progressions
- Section-aware intensity and density variations
"""

import random
import pretty_midi
from utils import get_scale_notes, NOTE_MAP
from style_library import (
    DRUM_NOTES, DRUM_STYLE_CONFIGS, BASS_THEORY_CONFIGS,
    DEFAULT_DRUM_CONFIG, DEFAULT_BASS_CONFIG
)
from instrument_map import select_instrument_for_role, get_instrument_program, normalize_instrument_name


# ============================================================================
# INTERVAL MAPPINGS FOR BASS THEORY
# ============================================================================
INTERVAL_MAP = {
    "root": 0,
    "minor_second": 1,
    "major_second": 2,
    "second": 2,
    "minor_third": 3,
    "third": 4,  # major third default
    "perfect_fourth": 5,
    "fourth": 5,
    "tritone": 6,
    "perfect_fifth": 7,
    "fifth": 7,
    "minor_sixth": 8,
    "sixth": 9,
    "minor_seventh": 10,
    "seventh": 11,  # major seventh default
    "octave": 12,
    "ninth": 14,  # 12 + 2
    "eleventh": 17,  # 12 + 5
    "thirteenth": 21,  # 12 + 9
}

# Note duration in steps (16th notes)
NOTE_LENGTH_MAP = {
    "sixteenth": 1,
    "dotted_sixteenth": 1.5,
    "eighth": 2,
    "dotted_eighth": 3,
    "quarter": 4,
    "dotted_quarter": 6,
    "half": 8,
    "dotted_half": 12,
    "whole": 16,
    "double_whole": 32,
}


# ============================================================================
# DRUM GENERATION
# ============================================================================

def get_drum_config(style_name):
    """Get drum configuration for a style, with fallback to defaults."""
    return DRUM_STYLE_CONFIGS.get(style_name, DEFAULT_DRUM_CONFIG)


def apply_humanization(time, velocity, config, step_duration):
    """Apply timing and velocity humanization to a note."""
    human = config.get("humanization", {})
    timing_jitter = human.get("timing_jitter", 0.0)
    velocity_jitter = human.get("velocity_jitter", 0.0)
    
    # Apply timing jitter
    if timing_jitter > 0:
        time += random.uniform(-timing_jitter, timing_jitter) * step_duration
    
    # Apply velocity jitter
    if velocity_jitter > 0:
        jitter_range = int(velocity * velocity_jitter)
        velocity = max(1, min(127, velocity + random.randint(-jitter_range, jitter_range)))
    
    return time, velocity


def apply_swing(time, step_index, config, step_duration):
    """Apply swing to off-beat notes."""
    human = config.get("humanization", {})
    swing_amount = human.get("swing_amount", 0.0)
    
    if swing_amount > 0 and step_index % 2 == 1:  # Apply to off-beats
        time += swing_amount * step_duration * 0.5
    
    return time


def get_section_density_modifier(config, section_type):
    """Get density modifier for a section type."""
    section_vars = config.get("section_variations", {})
    if section_type in section_vars:
        return section_vars[section_type].get("density_modifier", 1.0)
    # Fallback to 'default' or return 1.0
    return section_vars.get("default", {}).get("density_modifier", 1.0)


def get_patterns_for_section(config, section_type):
    """Get list of patterns to use for a section."""
    section_vars = config.get("section_variations", {})
    if section_type in section_vars:
        return section_vars[section_type].get("use_patterns", ["basic"])
    return section_vars.get("default", {}).get("use_patterns", ["basic"])


def generate_drums(pm, spec, section, t0):
    """
    Generate drum patterns based on style configurations.
    
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
    step_duration = 60 / bpm / 4  # 16th note duration
    steps_per_bar = 16
    total_bars = section["bars"]
    total_steps = total_bars * steps_per_bar
    
    # Get style and section info
    style_name = spec.get("identity", {}).get("style", "")
    section_type = section.get("type", "verse")
    intensity = section.get("intensity", 0.5)
    
    # Get drum config for style
    drum_config = get_drum_config(style_name)
    patterns = drum_config.get("patterns", {})
    velocities = drum_config.get("velocities", {})
    fill_config = drum_config.get("fills", {})
    
    # Get section-specific settings
    density_modifier = get_section_density_modifier(drum_config, section_type)
    available_patterns = get_patterns_for_section(drum_config, section_type)
    
    # Calculate effective density
    base_density = spec.get("style_params", {}).get("drum_density", 0.7)
    effective_density = base_density * density_modifier * (0.5 + intensity * 0.5)
    effective_density = min(1.0, effective_density)
    
    kicks = []
    current_pattern_name = "basic"
    pattern_change_interval = random.randint(4, 8)  # Change pattern every 4-8 bars
    pattern_bar_count = 0
    
    for bar in range(total_bars):
        # Select pattern for this bar
        pattern_bar_count += 1
        if pattern_bar_count >= pattern_change_interval:
            pattern_bar_count = 0
            pattern_change_interval = random.randint(4, 8)
            current_pattern_name = random.choice(available_patterns)
        
        # Get current pattern
        pattern = patterns.get(current_pattern_name, patterns.get("basic", {}))
        
        # Check if we should play a fill at phrase boundary
        is_phrase_end = (bar + 1) % 4 == 0 and bar < total_bars - 1
        use_fill = is_phrase_end and random.random() < fill_config.get("frequency", 0.3)
        fill_patterns = fill_config.get("patterns", [])
        
        if use_fill and fill_patterns:
            pattern = random.choice(fill_patterns)
        
        # Process each step in the bar
        for step_in_bar in range(steps_per_bar):
            global_step = bar * steps_per_bar + step_in_bar
            t = t0 + global_step * step_duration
            
            # Apply swing
            t = apply_swing(t, step_in_bar, drum_config, step_duration)
            
            # Process each drum voice in the pattern
            for voice_name, voice_pattern in pattern.items():
                if voice_name not in DRUM_NOTES:
                    continue
                
                if step_in_bar < len(voice_pattern) and voice_pattern[step_in_bar]:
                    # Check density for this hit
                    if random.random() > effective_density:
                        continue
                    
                    # Get velocity for this voice
                    vel_key = f"{voice_name}_base"
                    base_vel = velocities.get(vel_key, 80)
                    
                    # Check if this is a ghost note (pattern value < 100)
                    pattern_val = voice_pattern[step_in_bar]
                    is_ghost = isinstance(pattern_val, (int, float)) and pattern_val < 100 and pattern_val > 0
                    
                    if is_ghost:
                        vel = pattern_val
                    else:
                        # Apply intensity and variation
                        vel_range = velocities.get("hihat_variation", 20) if "hihat" in voice_name else 0
                        vel = base_vel + random.randint(-vel_range, vel_range)
                        vel = int(vel * (0.7 + intensity * 0.3))
                    
                    # Apply humanization
                    t_final, vel_final = apply_humanization(t, int(vel), drum_config, step_duration)
                    vel_final = max(1, min(127, vel_final))
                    
                    # Add note
                    note_duration = step_duration * 0.8  # Slightly shorter than step
                    inst.notes.append(pretty_midi.Note(vel_final, DRUM_NOTES[voice_name], t_final, t_final + note_duration))
                    
                    # Track kick times
                    if voice_name == "kick":
                        kicks.append(t_final)
    
    pm.instruments.append(inst)
    end_time = t0 + total_steps * step_duration
    return end_time, kicks


# ============================================================================
# BASS GENERATION - MUSIC THEORY AWARE
# ============================================================================

def get_bass_config(style_name):
    """Get bass theory configuration for a style."""
    return BASS_THEORY_CONFIGS.get(style_name, DEFAULT_BASS_CONFIG)


def get_scale_intervals(scale_type="natural_minor"):
    """Get interval structure for a scale."""
    from utils import get_scale_notes
    # Get scale starting from C (60)
    scale_notes = get_scale_notes("C_major", scale_type)
    # Convert to intervals from root
    root = scale_notes[0]
    return [n - root for n in scale_notes]


def get_chord_tones(chord_notes, root_midi):
    """Extract chord tones as intervals from root."""
    intervals = []
    for note in chord_notes:
        interval = (note - root_midi) % 12
        if interval not in intervals:
            intervals.append(interval)
    return intervals


def select_bass_note(chord_notes, scale_notes, config, step_index, intensity):
    """
    Select a bass note based on music theory and style configuration.
    
    Args:
        chord_notes: Current chord notes
        scale_notes: Scale notes for the key
        config: Bass theory configuration
        step_index: Position in the pattern (for variation)
        intensity: Section intensity (0-1)
    
    Returns:
        int: MIDI note number for bass
    """
    approach = config.get("approach", "simple")
    preferences = config.get("scale_preference", ["root", "fifth", "octave"])
    syncopation = config.get("syncopation", 0.3)
    octave_range = config.get("octave_range", (1, 2))
    
    # Get root from chord (lowest note)
    root_midi = min(chord_notes) if chord_notes else scale_notes[0]
    root_note = root_midi % 12
    
    # Determine which intervals to use based on approach
    available_intervals = []
    
    if approach in ["chord_tones", "simple", "four_on_floor", "driving"]:
        # Prefer chord tones
        chord_intervals = get_chord_tones(chord_notes, root_midi)
        for pref in preferences:
            if pref in INTERVAL_MAP:
                interval = INTERVAL_MAP[pref] % 12
                if interval in chord_intervals:
                    available_intervals.append(INTERVAL_MAP[pref])
        # Fallback to any chord tone
        if not available_intervals:
            available_intervals = [i if i < 12 else i - 12 for i in chord_intervals]
    
    elif approach == "walking":
        # Use scale tones with approach patterns
        for pref in preferences:
            if pref in INTERVAL_MAP:
                available_intervals.append(INTERVAL_MAP[pref])
    
    elif approach in ["groovy", "funky", "slap"]:
        # Mix of chord tones and approach notes
        chord_intervals = get_chord_tones(chord_notes, root_midi)
        for pref in preferences:
            if pref in INTERVAL_MAP:
                available_intervals.append(INTERVAL_MAP[pref])
        # Add some chromatic approach notes
        if random.random() < syncopation * intensity:
            available_intervals.append(random.choice([1, 6, 10]))
    
    elif approach == "rolling":
        # Fast patterns with scale tones
        for pref in preferences:
            if pref in INTERVAL_MAP:
                available_intervals.append(INTERVAL_MAP[pref])
    
    elif approach == "wobble":
        # Sub-bass with wobble
        available_intervals = [0, 7, 3]  # Root, fifth, minor third
        if random.random() < config.get("wobble_rate", 0.3):
            available_intervals.append(random.choice([-1, 1]))  # Slight wobble
    
    elif approach == "arpeggiated":
        # Arpeggio patterns
        chord_intervals = get_chord_tones(chord_notes, root_midi)
        available_intervals = sorted(chord_intervals + [i + 12 for i in chord_intervals])
    
    elif approach in ["experimental", "glitchy"]:
        # More dissonant intervals
        available_intervals = [INTERVAL_MAP.get(p, 0) for p in preferences]
    
    else:  # drone, minimal, orchestral, etc.
        available_intervals = [0]  # Just root
    
    # Select interval
    if not available_intervals:
        available_intervals = [0]
    
    selected_interval = random.choice(available_intervals)
    
    # Determine octave
    octave = random.randint(octave_range[0], octave_range[1])
    
    # Calculate final note
    bass_note = root_midi + selected_interval + (octave - 1) * 12
    
    # Clamp to reasonable bass range (C0 to C4)
    bass_note = max(24, min(84, bass_note))
    
    return bass_note


def get_note_duration(config, step_duration):
    """Get a note duration based on style configuration."""
    note_lengths = config.get("note_lengths", ["quarter"])
    length_name = random.choice(note_lengths)
    steps = NOTE_LENGTH_MAP.get(length_name, 4)
    return steps * step_duration


def generate_bass(pm, spec, section, t0, kicks, current_chords=None):
    """
    Generate bass lines based on style configurations and music theory.
    
    Args:
        pm: PrettyMIDI object
        spec: Full specification including style_params
        section: Section definition (type, bars, intensity)
        t0: Start time in seconds
        kicks: List of kick drum times for synchronization
        current_chords: Optional list of chords for the section
    """
    style_name = spec.get("identity", {}).get("style", "")
    section_type = section.get("type", "verse")
    intensity = section.get("intensity", 0.5)
    
    # Get bass config for style
    bass_config = get_bass_config(style_name)
    
    # Get musical context
    key = spec.get("identity", {}).get("key", "C_minor")
    scale_type = spec.get("identity", {}).get("scale_type", "natural_minor")
    scale_notes = get_scale_notes(key, scale_type)
    
    # Get root MIDI note (bass octave)
    root_key = key.split("_")[0]
    root_midi = NOTE_MAP.get(root_key, 48)  # C2 = 48
    
    # Select bass instrument (with random alternative if available)
    style_instruments = spec.get("style_params", {}).get("instruments", {})
    bass_instrument = select_instrument_for_role("bass", style_instruments, use_random=True)
    bass_instrument = normalize_instrument_name(bass_instrument)
    program = get_instrument_program(bass_instrument)
    
    inst = pretty_midi.Instrument(program=program)
    
    bpm = spec["time"]["bpm"]
    step_duration = 60 / bpm / 4  # 16th note
    bar_duration = step_duration * 16
    
    # Get rhythm parameters
    rhythmic_density = bass_config.get("rhythmic_density", 0.5)
    syncopation = bass_config.get("syncopation", 0.3)
    variation_on_repeat = bass_config.get("variation_on_repeat", False)
    
    # Build chord progression for the section
    if current_chords is None:
        # Generate simple progression based on scale
        num_chords = section["bars"]
        current_chords = []
        for i in range(num_chords):
            degree = i % 7
            chord = [scale_notes[degree], scale_notes[(degree + 2) % 7], 
                     scale_notes[(degree + 4) % 7]]
            current_chords.append(chord)
    
    # Generate bass pattern for each bar
    for bar_idx in range(section["bars"]):
        chord = current_chords[bar_idx % len(current_chords)]
        bar_start = t0 + bar_idx * bar_duration
        
        # Determine how many notes to play in this bar
        notes_in_bar = max(1, int(4 * rhythmic_density * (0.5 + intensity * 0.5)))
        
        # Generate note positions
        if bass_config.get("approach") == "four_on_floor":
            # Steady quarter notes
            note_positions = [i * step_duration * 4 for i in range(4)]
        elif bass_config.get("approach") in ["driving", "rolling"]:
            # Eighth notes
            note_positions = [i * step_duration * 2 for i in range(8)]
        elif bass_config.get("approach") in ["walking"]:
            # Quarter notes
            note_positions = [i * step_duration * 4 for i in range(4)]
        else:
            # Variable positions based on density and syncopation
            note_positions = []
            for step in range(16):
                # Strong beats are more likely
                is_strong_beat = step % 4 == 0
                prob = rhythmic_density * (1.5 if is_strong_beat else 0.5)
                prob *= (0.5 + intensity * 0.5)
                
                if random.random() < prob:
                    note_positions.append(step * step_duration)
                
                # Add syncopated notes
                if not is_strong_beat and random.random() < syncopation * rhythmic_density:
                    note_positions.append(step * step_duration)
        
        # Limit notes and sort
        note_positions = sorted(set(note_positions))[:notes_in_bar * 2]
        
        if not note_positions:
            note_positions = [0]  # At least one note
        
        # Generate notes
        prev_note = None
        for i, pos in enumerate(note_positions):
            note_time = bar_start + pos
            
            # Select note based on music theory
            note = select_bass_note(chord, scale_notes, bass_config, i, intensity)
            
            # Apply approach patterns
            approach_patterns = bass_config.get("approach_patterns", ["direct"])
            if random.random() < 0.3 and i > 0:
                pattern = random.choice(approach_patterns)
                if pattern == "chromatic_below":
                    note = note - 1
                elif pattern == "chromatic_above":
                    note = note + 1
                elif pattern == "diatonic_below":
                    note = note - 2
                elif pattern == "diatonic_above":
                    note = note + 2
                elif pattern == "octave_leap":
                    note = note + 12 * random.choice([-1, 1])
                elif pattern == "slide":
                    # Slide is handled by note duration overlap
                    pass
            
            # Calculate velocity based on position and intensity
            is_strong_beat = (pos / step_duration) % 4 == 0
            base_velocity = 80 + int(30 * intensity)
            if is_strong_beat:
                velocity = base_velocity + 10
            else:
                velocity = base_velocity - 10
            
            # Add variation
            velocity += random.randint(-15, 15)
            velocity = max(30, min(120, velocity))
            
            # Calculate duration
            if i < len(note_positions) - 1:
                duration = (note_positions[i + 1] - pos) * 0.8
            else:
                duration = get_note_duration(bass_config, step_duration)
            
            # Ensure notes don't overlap unnaturally (except for slides)
            if prev_note and note_time < prev_note[0] + prev_note[1]:
                if bass_config.get("slide_frequency", 0) < random.random():
                    # Overlap for slide effect
                    duration = prev_note[0] + prev_note[1] - note_time + duration * 0.5
            
            inst.notes.append(pretty_midi.Note(velocity, note, note_time, note_time + duration))
            prev_note = (note_time, duration)
    
    pm.instruments.append(inst)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def generate_drums_and_bass(pm, spec, section, t0, current_chords=None):
    """
    Generate both drums and bass for a section.
    
    Args:
        pm: PrettyMIDI object
        spec: Full specification
        section: Section definition
        t0: Start time
        current_chords: Optional chord progression for bass
    
    Returns:
        tuple: (end_time, kicks)
    """
    end_time, kicks = generate_drums(pm, spec, section, t0)
    generate_bass(pm, spec, section, t0, kicks, current_chords)
    return end_time, kicks