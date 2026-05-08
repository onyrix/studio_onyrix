"""
Audio Rendering Module - Convert MIDI to WAV with proper error handling

This module provides:
1. Robust MIDI to audio synthesis with error handling
2. Volume normalization and mixing
3. Proper handling of drum tracks
4. Quality control checks
"""

import pretty_midi
import soundfile as sf
import numpy as np
import os


def render_to_audio(pm, filename="output/output.wav", normalize=True, volume_balance=None):
    """
    Render a PrettyMIDI object to audio with proper error handling.
    
    Args:
        pm: PrettyMIDI object to render
        filename: Output WAV file path
        normalize: Whether to normalize the audio (default: True)
        volume_balance: Optional dict to adjust volume per instrument type
                       e.g., {"drums": 0.8, "bass": 0.9, "other": 1.0}
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Validate the MIDI object
        if not pm or not pm.instruments:
            print("Error: Empty MIDI object, nothing to render")
            return False
        
        print(f"Rendering {len(pm.instruments)} tracks to audio...")
        
        # Check for common issues before rendering
        _validate_midi(pm)
        
        # Synthesize audio
        try:
            audio = pm.synthesize()
        except Exception as e:
            print(f"Error during synthesis: {e}")
            # Try with a simpler approach
            audio = _fallback_synthesize(pm)
            if audio is None:
                print("Failed to synthesize audio")
                return False
        
        # Apply volume balancing if requested
        if volume_balance:
            audio = _apply_volume_balance(pm, audio, volume_balance)
        
        # Normalize audio if requested
        if normalize and np.max(np.abs(audio)) > 0:
            audio = _normalize_audio(audio)
        
        # Write to file
        sf.write(filename, audio, 44100)
        
        # Verify the file was written
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            duration = len(audio) / 44100
            print(f"Audio rendered successfully: {filename}")
            print(f"  Duration: {duration:.2f} seconds")
            print(f"  File size: {file_size / 1024:.1f} KB")
            print(f"  Sample rate: 44100 Hz")
            print(f"  Channels: {1 if audio.ndim == 1 else audio.shape[1]}")
            return True
        else:
            print(f"Error: File {filename} was not created")
            return False
            
    except Exception as e:
        print(f"Unexpected error during audio rendering: {e}")
        import traceback
        traceback.print_exc()
        return False


def _validate_midi(pm):
    """
    Validate MIDI object and fix common issues.
    
    Args:
        pm: PrettyMIDI object to validate
    """
    issues_found = []
    
    # Check for empty tracks
    for i, inst in enumerate(pm.instruments):
        if not inst.notes:
            issues_found.append(f"Track {i} ({inst.name or 'unnamed'}) has no notes")
    
    # Check for drum track issues
    drum_tracks = [inst for inst in pm.instruments if inst.is_drum]
    if drum_tracks:
        for i, drum in enumerate(drum_tracks):
            # Verify drum notes are in valid range (typically 27-87 for GM)
            for note in drum.notes:
                if note.pitch < 27 or note.pitch > 87:
                    issues_found.append(
                        f"Drum note pitch {note.pitch} may be out of typical range (27-87)"
                    )
                    # Fix: clamp to valid range
                    note.pitch = max(27, min(87, note.pitch))
    
    # Check for overlapping notes that might cause issues
    for inst in pm.instruments:
        if len(inst.notes) > 1:
            # Sort notes by start time
            inst.notes.sort(key=lambda n: n.start)
            # Check for extreme overlaps
            for j in range(len(inst.notes) - 1):
                curr = inst.notes[j]
                next_note = inst.notes[j + 1]
                if curr.end > next_note.start + 10:  # More than 10 seconds overlap
                    issues_found.append(
                        f"Track has notes with extreme overlap ({curr.end - next_note.start:.1f}s)"
                    )
    
    # Report issues (but don't fail)
    if issues_found:
        print("MIDI validation warnings:")
        for issue in issues_found[:5]:  # Show first 5 issues
            print(f"  - {issue}")
        if len(issues_found) > 5:
            print(f"  ... and {len(issues_found) - 5} more issues")


def _fallback_synthesize(pm):
    """
    Fallback synthesis method if the standard one fails.
    Creates a simple sine wave synthesis.
    
    Args:
        pm: PrettyMIDI object
    
    Returns:
        numpy array of audio samples
    """
    print("Using fallback synthesis method...")
    
    sr = 44100
    duration = pm.get_end_time()
    num_samples = int(duration * sr)
    audio = np.zeros(num_samples, dtype=np.float32)
    
    # Simple volume envelope to avoid clicks
    def envelope(t, duration, attack=0.01, decay=0.1, sustain=0.7, release=0.1):
        if t < attack:
            return t / attack
        elif t < attack + decay:
            return 1.0 - (1.0 - sustain) * ((t - attack) / decay)
        elif t > duration - release:
            return sustain * (duration - t) / release
        else:
            return sustain
    
    # Render each instrument
    for inst in pm.instruments:
        # Determine volume based on instrument type
        if inst.is_drum:
            volume = 0.3  # Drums are percussive, so lower volume
        else:
            volume = 0.15  # Other instruments
        
        # Simple frequency to MIDI note conversion
        for note in inst.notes:
            freq = 440 * (2 ** ((note.pitch - 69) / 12))
            start_sample = int(note.start * sr)
            end_sample = int(min(note.end * sr, num_samples))
            
            if start_sample >= num_samples:
                continue
            
            # Generate sine wave
            t = np.arange(end_sample - start_sample) / sr
            note_audio = np.sin(2 * np.pi * freq * t)
            
            # Apply envelope
            note_duration = note.end - note.start
            env = np.array([envelope(t_i, note_duration) for t_i in t])
            note_audio *= env
            
            # Apply velocity
            velocity_factor = note.velocity / 127.0
            note_audio *= velocity_factor * volume
            
            # Add to mix
            audio[start_sample:end_sample] += note_audio
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.9
    
    return audio


def _normalize_audio(audio, target_db=-1.0):
    """
    Normalize audio to a target dB level.
    
    Args:
        audio: Audio samples
        target_db: Target peak level in dB (default: -1.0 dB)
    
    Returns:
        Normalized audio
    """
    peak = np.max(np.abs(audio))
    if peak == 0:
        return audio
    
    # Convert target dB to linear
    target_linear = 10 ** (target_db / 20)
    
    # Calculate current peak in dB
    current_db = 20 * np.log10(peak)
    
    # Calculate gain needed
    gain_db = target_db - current_db
    gain_linear = 10 ** (gain_db / 20)
    
    # Apply gain
    normalized = audio * gain_linear
    
    # Ensure we don't clip
    normalized = np.clip(normalized, -1.0, 1.0)
    
    return normalized


def _apply_volume_balance(pm, audio, balance):
    """
    Apply volume balancing to different instrument types.
    This is a simplified version - proper implementation would require
    rendering each track separately and mixing.
    
    Args:
        pm: PrettyMIDI object
        audio: Rendered audio
        balance: Dict with volume multipliers per instrument type
    
    Returns:
        Balanced audio (may be same as input if balancing not possible)
    """
    # For now, just return the audio as-is
    # A more advanced implementation would render tracks separately
    return audio


def render_with_separate_tracks(pm, filename="output/output.wav"):
    """
    Render MIDI to audio with each track rendered separately for better mixing control.
    
    Args:
        pm: PrettyMIDI object
        filename: Output WAV file path
    
    Returns:
        bool: True if successful
    """
    try:
        # Render each track separately
        track_audios = []
        track_volumes = {
            'drum': 0.7,    # Drums slightly quieter
            'bass': 0.9,    # Bass prominent
            'lead': 0.8,    # Lead clear but not overpowering
            'pad': 0.6,     # Pads in background
            'other': 0.7,   # Everything else
        }
        
        for inst in pm.instruments:
            # Create a single-track MIDI
            single_track_pm = pretty_midi.PrettyMIDI()
            single_track_pm.instruments.append(inst)
            
            try:
                track_audio = single_track_pm.synthesize()
                
                # Determine track type for volume adjustment
                if inst.is_drum:
                    track_type = 'drum'
                else:
                    # Try to guess track type from program number
                    program = inst.program
                    if 32 <= program <= 39:  # Bass range
                        track_type = 'bass'
                    elif 80 <= program <= 87:  # Lead range
                        track_type = 'lead'
                    elif 88 <= program <= 95:  # Pad range
                        track_type = 'pad'
                    else:
                        track_type = 'other'
                
                # Apply volume adjustment
                volume = track_volumes.get(track_type, 0.7)
                track_audio *= volume
                
                track_audios.append(track_audio)
                
            except Exception as e:
                print(f"Warning: Failed to render track {inst.name}: {e}")
                continue
        
        if not track_audios:
            print("No tracks were rendered successfully")
            return False
        
        # Mix all tracks together
        max_length = max(len(audio) for audio in track_audios)
        mixed_audio = np.zeros(max_length, dtype=np.float32)
        
        for track_audio in track_audios:
            # Pad shorter tracks with zeros
            if len(track_audio) < max_length:
                padded = np.zeros(max_length, dtype=np.float32)
                padded[:len(track_audio)] = track_audio
                track_audio = padded
            
            mixed_audio += track_audio
        
        # Normalize the mix
        mixed_audio = _normalize_audio(mixed_audio)
        
        # Write to file
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        sf.write(filename, mixed_audio, 44100)
        
        print(f"Multi-track audio rendered: {filename}")
        print(f"  Tracks mixed: {len(track_audios)}")
        return True
        
    except Exception as e:
        print(f"Error in multi-track rendering: {e}")
        return False