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
    """Apply timing and velocity humanization to a note.
    For drums, velocity jitter is minimal to maintain audibility."""
    human = config.get("humanization", {})
    timing_jitter = human.get("timing_jitter", 0.0)
    velocity_jitter = human.get("velocity_jitter", 0.0)
    
    # Apply timing jitter (keep this)
    if timing_jitter > 0:
        time += random.uniform(-timing_jitter, timing_jitter) * step_duration
    
    # Apply MINIMAL velocity jitter for drums (preserve audibility)
    if velocity_jitter > 0:
        # Very small jitter range for drums (±5 max)
        jitter_range = min(5, int(velocity * 0.1))  # Max 10% or 5
        velocity = max(60, min(127, velocity + random.randint(-jitter_range, jitter_range)))
    else:
        # No jitter, just ensure minimum
        velocity = max(60, min(127, velocity))
    
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


# Pattern key aliases (human-friendly -> DRUM_NOTES keys)
PATTERN_KEY_ALIASES = {
    "hihat": "hihat_closed",
    "hihat_closed": "hihat_closed",
    "hihat_open": "hihat_open",
    "kick": "kick",
    "snare": "snare",
    "clap": "clap",
    "crash": "crash",
    "ride": "ride",
    "tom_high": "tom_high",
    "tom_mid": "tom_mid",
    "tom_low": "tom_low",
    "cowbell": "cowbell",
    "click": "click",
}


def resolve_pattern_voice(voice_name):
    """Resolve a pattern voice name to a DRUM_NOTES key."""
    if voice_name in DRUM_NOTES:
        return voice_name
    return PATTERN_KEY_ALIASES.get(voice_name)


def generate_drums(pm, spec, section, t0):
    """
    Generate drum patterns based on style configurations.
    Enhanced version with proper pattern key resolution and stronger velocities.
    
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
    
    # Calculate effective density - ensure drums are always audible
    base_density = spec.get("style_params", {}).get("drum_density", 0.7)
    effective_density = base_density * density_modifier * (0.7 + intensity * 0.3)
    effective_density = min(1.0, max(0.5, effective_density))  # At least 0.5 density
    
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
                # Resolve voice name to DRUM_NOTES key
                resolved_voice = resolve_pattern_voice(voice_name)
                if resolved_voice is None or resolved_voice not in DRUM_NOTES:
                    continue
                
                if step_in_bar < len(voice_pattern) and voice_pattern[step_in_bar]:
                    # Check density for this hit
                    if random.random() > effective_density:
                        continue
                    
                    # Get base velocity for this voice - VERY STRONG
                    vel_key = f"{resolved_voice}_base"
                    base_vel = velocities.get(vel_key, 90)
                    
                    # For drums, ALWAYS use base_vel as minimum (pattern value 1 = trigger)
                    # This ensures loud, audible drums
                    vel = base_vel
                    
                    # Add small random variation
                    variation = random.randint(-5, 5)
                    vel = vel + variation
                    
                    # Apply intensity multiplier for THIS instrument type
                    if "kick" in resolved_voice:
                        vel = int(vel * (1.0 + intensity * 0.5))  # Kick: VERY LOUD
                        vel = max(110, min(127, vel))  # Kick at least 110
                    elif "snare" in resolved_voice or "clap" in resolved_voice:
                        vel = int(vel * (0.9 + intensity * 0.4))
                        vel = max(100, min(127, vel))  # Snare at least 100
                    elif "hihat" in resolved_voice:
                        vel = int(vel * (0.8 + intensity * 0.3))
                        vel = max(80, min(127, vel))  # Hihat at least 80
                    else:
                        vel = int(vel * (0.9 + intensity * 0.3))
                        vel = max(90, min(127, vel))  # Others at least 90
                    
                    # Apply minimal humanization (preserve velocity)
                    t_final, vel_final = apply_humanization(t, int(vel), drum_config, step_duration)
                    # Final safety: ensure VERY audible (minimum 60, but instrument-specific minimum already applied)
                    vel_final = max(vel_final, 60)
                    
                    # Add note
                    note_duration = step_duration * 0.9  # Slightly shorter than step
                    inst.notes.append(pretty_midi.Note(vel_final, DRUM_NOTES[resolved_voice], t_final, t_final + note_duration))
                    
                    # Track kick times
                    if resolved_voice == "kick":
                        kicks.append(t_final)
    
    # Fallback: if no drum notes were generated, add a basic kick pattern
    if len(inst.notes) == 0:
        print("Warning: No drum notes generated, adding fallback kick pattern")
        for bar in range(total_bars):
            for beat in [0, 2]:  # Kick on beats 1 and 3
                t = t0 + (bar * steps_per_bar + beat * 4) * step_duration
                inst.notes.append(pretty_midi.Note(100, DRUM_NOTES["kick"], t, t + step_duration * 0.9))
    
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


def select_bass_note(root_note_class, chord_notes, scale_notes, config, step_index, intensity):
    """
    Select a bass note based on music theory and style configuration.
    
    Args:
        root_note_class: Root note class (0-11, where 0=C)
        chord_notes: Current chord notes (for determining chord tones)
        scale_notes: Scale notes for the key
        config: Bass theory configuration
        step_index: Position in the pattern (for variation)
        intensity: Section intensity (0-1)
    
    Returns:
        int: MIDI note number for bass (in bass range C1-C3)
    """
    approach = config.get("approach", "simple")
    preferences = config.get("scale_preference", ["root", "fifth", "octave"])
    syncopation = config.get("syncopation", 0.3)
    octave_range = config.get("octave_range", (1, 2))
    
    # Determine which intervals to use based on approach
    available_intervals = []
    
    if approach in ["chord_tones", "simple", "four_on_floor", "driving"]:
        # Prefer chord tones - extract intervals from chord
        if chord_notes:
            chord_root = min(chord_notes)
            chord_intervals = get_chord_tones(chord_notes, chord_root)
            for pref in preferences:
                if pref in INTERVAL_MAP:
                    interval = INTERVAL_MAP[pref] % 12
                    if interval in chord_intervals:
                        available_intervals.append(INTERVAL_MAP[pref])
            # Fallback to any chord tone
            if not available_intervals:
                available_intervals = [i if i < 12 else i - 12 for i in chord_intervals]
        else:
            available_intervals = [INTERVAL_MAP.get(p, 0) for p in preferences]
    
    elif approach == "walking":
        # Use scale tones with approach patterns
        for pref in preferences:
            if pref in INTERVAL_MAP:
                available_intervals.append(INTERVAL_MAP[pref])
    
    elif approach in ["groovy", "funky", "slap"]:
        # Mix of chord tones and approach notes
        if chord_notes:
            chord_root = min(chord_notes)
            chord_intervals = get_chord_tones(chord_notes, chord_root)
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
        if chord_notes:
            chord_root = min(chord_notes)
            chord_intervals = get_chord_tones(chord_notes, chord_root)
            available_intervals = sorted(chord_intervals + [i + 12 for i in chord_intervals])
        else:
            available_intervals = [0, 12]
    
    elif approach in ["experimental", "glitchy"]:
        # More dissonant intervals
        available_intervals = [INTERVAL_MAP.get(p, 0) for p in preferences]
    
    else:  # drone, minimal, orchestral, etc.
        available_intervals = [0]  # Just root
    
    # Select interval
    if not available_intervals:
        available_intervals = [0]
    
    selected_interval = random.choice(available_intervals)
    
    # Determine octave (1 = C2, 2 = C3, etc.)
    octave = random.randint(octave_range[0], octave_range[1])
    
    # Calculate final note in bass range
    # root_note_class is 0-11 (C=0, C#=1, etc.)
    # octave 1 = C1 (36), octave 2 = C2 (48), octave 3 = C3 (60)
    # Formula: root_note_class + (octave * 12) + 24 = starts at C1=36
    bass_note = root_note_class + (octave * 12) + 24 + selected_interval
    
    # Clamp to reasonable bass range (C1 to C3)
    bass_note = max(36, min(60, bass_note))
    
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
    Enhanced version with stronger velocities and better drum synchronization.
    
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
    
    # Get root MIDI note (bass octave) - ensure proper bass range
    root_key = key.split("_")[0]
    root_note_class = NOTE_MAP.get(root_key, 48)  # C = 48 (C4)
    # Put in bass range (C1-C2 typically): C1=36, C2=48
    root_midi = (root_note_class % 12) + 36  # Base: C1 = 36
    
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
            # Get root note class from the chord's root
            chord_root = min(chord) % 12 if chord else root_note_class
            note = select_bass_note(chord_root, chord, scale_notes, bass_config, i, intensity)
            
            # Apply approach patterns
            approach_patterns = bass_config.get("approach_patterns", ["direct"])
            if random.random() < 0.3 and i > 0:
                pattern = random.choice(approach_patterns)
                if pattern == "chromatic_below":
                    note = max(36, note - 1)  # Don't go below C1
                elif pattern == "chromatic_above":
                    note = min(60, note + 1)  # Don't go above C3
                elif pattern == "diatonic_below":
                    note = max(36, note - 2)
                elif pattern == "diatonic_above":
                    note = min(60, note + 2)
                elif pattern == "octave_leap":
                    leap = note + 12 * random.choice([-1, 1])
                    note = max(36, min(60, leap))  # Keep in bass range
                elif pattern == "slide":
                    # Slide is handled by note duration overlap
                    pass
            
            # Calculate velocity based on position and intensity - STRONGER
            is_strong_beat = (pos / step_duration) % 4 == 0
            base_velocity = 100 + int(30 * intensity)  # Even higher base velocity
            if is_strong_beat:
                velocity = base_velocity + 20
            else:
                velocity = base_velocity
            
            # Add variation
            velocity += random.randint(-5, 5)  # Less variation to maintain audibility
            velocity = max(80, min(127, velocity))  # Higher minimum (80) for audibility
            
            # Calculate duration - longer notes for better audibility
            if i < len(note_positions) - 1:
                duration = (note_positions[i + 1] - pos) * 0.95  # Slightly longer
            else:
                duration = get_note_duration(bass_config, step_duration) * 1.5  # Longer sustain
            
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