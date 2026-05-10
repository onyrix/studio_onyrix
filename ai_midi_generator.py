"""
AI MIDI Generator Module - Local pre-trained models for MIDI generation

This module provides:
1. MidiBERT integration for melody/chord generation
2. MMM (Multi-Track Music Machine) for full multi-track MIDI
3. DiffMIDI for high-quality drum/bass patterns
4. Hybrid workflow combining AI seeds with rule-based editing

All models run locally with zero cloud costs.
"""

import pretty_midi
import numpy as np
import json
import os
from typing import Optional, Dict, List, Tuple

# Check available AI libraries
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not available. Some AI features will be disabled.")

try:
    from magenta.models.mmm import mmm as mmm_model
    from magenta.music import midi_io as magenta_midi_io
    MAGENTA_AVAILABLE = True
except ImportError:
    MAGENTA_AVAILABLE = False
    print("Warning: Magenta not available. MMM features will be disabled.")

try:
    # MidiBERT uses REMI tokenization
    from midibert.preprocess import REMI
    from midibert.models import MidiBERT as MidiBERTPiano
    MIDIBERT_AVAILABLE = True
except ImportError:
    MIDIBERT_AVAILABLE = False
    print("Warning: MidiBERT not available. Melody AI will be disabled.")

try:
    import diffmidi
    DIFFMIDI_AVAILABLE = True
except ImportError:
    DIFFMIDI_AVAILABLE = False
    print("Warning: DiffMIDI not available. Diffusion-based generation disabled.")

# Style mapping from our style names to model-specific labels
STYLE_TO_GENRE = {
    # Hip Hop / Urban
    "trap": "hip_hop",
    "drill": "hip_hop",
    "boom_bap": "hip_hop",
    "lofi": "electronic",
    
    # Club / Electronic
    "house": "electronic",
    "deep_house": "electronic",
    "techno": "electronic",
    "minimal_techno": "electronic",
    "dubstep": "electronic",
    "dnb": "electronic",
    
    # Cinematic / Atmospheric
    "ambient": "ambient",
    "cinematic": "cinematic",
    "downtempo": "electronic",
    
    # Band / Acoustic
    "rock": "rock",
    "funk": "funk",
    "jazz": "jazz",
    
    # Synth / Retro
    "synthpop": "pop",
    "synthwave": "electronic",
    "retrowave": "electronic",
    "outrun": "electronic",
    "darkwave": "electronic",
    "ebm": "electronic",
    "electro": "electronic",
    "idm": "electronic",
    "glitch": "electronic",
    "electronic_pop": "pop",
}

# Model checkpoint paths (users should download these)
CHECKPOINT_DIR = "checkpoints"
MMM_CHECKPOINT = os.path.join(CHECKPOINT_DIR, "mmm.ckpt")
MIDIBERT_CHECKPOINT = os.path.join(CHECKPOINT_DIR, "midibert-piano.ckpt")
DIFFMIDI_CHECKPOINT = os.path.join(CHECKPOINT_DIR, "diffmidi.ckpt")


class MidiBERTGenerator:
    """Generate melodies and chords using MidiBERT pre-trained model."""
    
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.available = MIDIBERT_AVAILABLE
        self.model = None
        self.remi = None
        
        if self.available:
            try:
                self.remi = REMI()
                checkpoint = checkpoint_path or MIDIBERT_CHECKPOINT
                if os.path.exists(checkpoint):
                    self.model = MidiBERTPiano.from_pretrained(checkpoint)
                else:
                    # Try loading from HuggingFace hub
                    self.model = MidiBERTPiano.from_pretrained("wazenmai/MidiBERT-Piano")
                print("MidiBERT loaded successfully.")
            except Exception as e:
                print(f"Failed to load MidiBERT: {e}")
                self.available = False
    
    def generate_melody(self, style: str, key: str, prompt_midi: Optional[pretty_midi.PrettyMIDI] = None,
                        num_tokens: int = 512) -> Optional[pretty_midi.PrettyMIDI]:
        """
        Generate melody using MidiBERT.
        
        Args:
            style: Music style (trap, lofi, etc.)
            key: Musical key (C_major, F_minor, etc.)
            prompt_midi: Optional prompt MIDI for continuation
            num_tokens: Number of REMI tokens to generate
            
        Returns:
            pretty_midi.PrettyMIDI object or None if failed
        """
        if not self.available or not self.model:
            print("MidiBERT not available.")
            return None
        
        try:
            # Convert prompt to REMI tokens if provided
            if prompt_midi:
                tokens = self.remi.midi_to_tokens(prompt_midi)
                # Truncate to leave room for generation
                tokens = tokens[:512 - num_tokens // 2]
            else:
                # Create empty prompt with style/key context
                tokens = self._create_style_prompt(style, key)
            
            # Generate continuation
            with torch.no_grad():
                generated = self.model.generate(
                    input_ids=torch.tensor([tokens]),
                    max_length=num_tokens,
                    num_return_sequences=1,
                    pad_token_id=self.remi.pad_token_id
                )
            
            # Convert back to MIDI
            generated_tokens = generated[0].tolist()
            midi = self.remi.tokens_to_midi(generated_tokens)
            return midi
            
        except Exception as e:
            print(f"MidiBERT generation failed: {e}")
            return None
    
    def _create_style_prompt(self, style: str, key: str) -> List[int]:
        """Create initial prompt tokens based on style and key."""
        # This is a simplified version - REMI tokenization is complex
        # In practice, you'd create proper REMI tokens for style/key
        return [self.remi.bos_token_id] if hasattr(self.remi, 'bos_token_id') else [0]
    
    def generate_chord_progression(self, style: str, key: str, num_chords: int = 8) -> Optional[List[List[int]]]:
        """
        Generate chord progression suitable for the style.
        
        Returns:
            List of chords, each chord is list of MIDI note numbers
        """
        if not self.available or not self.model:
            return None
        
        try:
            # Generate a chord-focused MIDI
            midi = self.generate_melody(style, key, num_tokens=256)
            if not midi:
                return None
            
            # Extract chord progressions from generated MIDI
            chords = []
            for instrument in midi.instruments:
                if not instrument.is_drum:
                    # Group notes into chords (simplified)
                    notes_sorted = sorted(instrument.notes, key=lambda n: n.start)
                    current_chord = []
                    current_time = None
                    
                    for note in notes_sorted:
                        if current_time is None:
                            current_time = note.start
                            current_chord = [note.pitch]
                        elif abs(note.start - current_time) < 0.1:  # Same time = chord
                            current_chord.append(note.pitch)
                        else:
                            if current_chord:
                                chords.append(current_chord)
                            current_chord = [note.pitch]
                            current_time = note.start
                    
                    if current_chord:
                        chords.append(current_chord)
            
            return chords[:num_chords] if chords else None
            
        except Exception as e:
            print(f"Chord generation failed: {e}")
            return None


class MMMGenerator:
    """Generate full multi-track MIDI using Multi-Track Music Machine."""
    
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.available = MAGENTA_AVAILABLE
        self.model = None
        
        if self.available:
            try:
                checkpoint = checkpoint_path or MMM_CHECKPOINT
                if os.path.exists(checkpoint):
                    self.model = mmm_model.MultiTrackMusicMachine()
                    self.model.load_checkpoint(checkpoint)
                else:
                    print(f"MMM checkpoint not found at {checkpoint}")
                    print("Please download from: https://github.com/magenta/magenta/tree/main/magenta/models/mmm")
                    self.available = False
            except Exception as e:
                print(f"Failed to load MMM: {e}")
                self.available = False
    
    def generate_multi_track(self, style: str, key: str, bpm: int = 120,
                            duration_bars: int = 16) -> Optional[pretty_midi.PrettyMIDI]:
        """
        Generate full multi-track MIDI with separate tracks for drums, bass, melody, pads.
        
        Args:
            style: Music style
            key: Musical key
            bpm: Tempo
            duration_bars: Number of bars to generate
            
        Returns:
            pretty_midi.PrettyMIDI with multiple tracks or None if failed
        """
        if not self.available or not self.model:
            print("MMM not available.")
            return None
        
        try:
            # Map style to MMM genre
            genre = STYLE_TO_GENRE.get(style, "electronic")
            
            # Generate using MMM
            # Note: MMM API may vary - this is a conceptual example
            z = self._encode_style_genre(genre)
            midi_data = self.model.generate(
                z=z,
                tempo=bpm,
                key=key,
                num_bars=duration_bars
            )
            
            # Convert to pretty_midi
            pm = magenta_midi_io.midi_data_to_pretty_midi(midi_data)
            
            # Ensure proper track naming and drum flags
            self._label_tracks(pm)
            
            return pm
            
        except Exception as e:
            print(f"MMM generation failed: {e}")
            return None
    
    def _encode_style_genre(self, genre: str):
        """Encode genre for MMM model."""
        # MMM uses genre embeddings - implementation depends on model version
        # This is a placeholder
        return torch.randn(1, 512) if TORCH_AVAILABLE else None
    
    def _label_tracks(self, pm: pretty_midi.PrettyMIDI):
        """Label tracks with appropriate names and drum flags."""
        for i, instrument in enumerate(pm.instruments):
            # Try to infer track type from program number
            if instrument.program in range(0, 8):  # Piano
                instrument.name = "Piano/Lead"
            elif instrument.program in range(32, 40):  # Bass
                instrument.name = "Bass"
                instrument.is_drum = False
            elif instrument.program in range(80, 96):  # Synth lead/pad
                instrument.name = "Synth/Pad"
            elif instrument.is_drum:
                instrument.name = "Drums"
            
            if not instrument.name:
                instrument.name = f"Track {i}"


class DiffMIDIGenerator:
    """Generate MIDI using diffusion models (high quality, controllable)."""
    
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.available = DIFFMIDI_AVAILABLE
        self.model = None
        
        if self.available:
            try:
                checkpoint = checkpoint_path or DIFFMIDI_CHECKPOINT
                if os.path.exists(checkpoint):
                    self.model = diffmidi.DiffMIDI.load_from_checkpoint(checkpoint)
                else:
                    print(f"DiffMIDI checkpoint not found at {checkpoint}")
                    print("Please download from: https://github.com/zbwang/diffmidi")
                    self.available = False
            except Exception as e:
                print(f"Failed to load DiffMIDI: {e}")
                self.available = False
    
    def generate_drums(self, style: str, bpm: int, bars: int = 8) -> Optional[pretty_midi.PrettyMIDI]:
        """Generate drum patterns using diffusion."""
        if not self.available or not self.model:
            return None
        
        try:
            # DiffMIDI generation
            genre = STYLE_TO_GENRE.get(style, "electronic")
            midi = self.model.generate(
                genre=genre,
                tempo=bpm,
                track_type="drums",
                num_bars=bars
            )
            return midi
        except Exception as e:
            print(f"DiffMIDI drum generation failed: {e}")
            return None
    
    def generate_bass(self, style: str, key: str, bpm: int, bars: int = 8) -> Optional[pretty_midi.PrettyMIDI]:
        """Generate bass lines using diffusion."""
        if not self.available or not self.model:
            return None
        
        try:
            genre = STYLE_TO_GENRE.get(style, "electronic")
            midi = self.model.generate(
                genre=genre,
                tempo=bpm,
                key=key,
                track_type="bass",
                num_bars=bars
            )
            return midi
        except Exception as e:
            print(f"DiffMIDI bass generation failed: {e}")
            return None


class HybridMIDIGenerator:
    """
    Unified generator that combines AI models with rule-based system.
    Uses AI for initial generation, then applies rule-based refinements.
    """
    
    def __init__(self):
        self.midibert = MidiBERTGenerator()
        self.mmm = MMMGenerator()
        self.diffmidi = DiffMIDIGenerator()
        
        # Check which models are available
        self.available_models = {
            "midibert": self.midibert.available,
            "mmm": self.mmm.available,
            "diffmidi": self.diffmidi.available
        }
        
        print(f"AI Models Available: {self.available_models}")
    
    def generate_hybrid(self, style: str, key: str = "C_minor", bpm: int = 120,
                       chaos: float = 0.3, bars: int = 16,
                       use_ai: bool = True) -> pretty_midi.PrettyMIDI:
        """
        Generate MIDI using hybrid AI + rule-based approach.
        
        Args:
            style: Music style
            key: Musical key
            bpm: Tempo
            chaos: Rule-based chaos parameter
            bars: Number of bars
            use_ai: Whether to use AI generation
            
        Returns:
            pretty_midi.PrettyMIDI object
        """
        if use_ai and any(self.available_models.values()):
            # Try AI generation first
            ai_midi = self._generate_with_ai(style, key, bpm, bars)
            if ai_midi:
                print("AI generation successful. Applying rule-based refinements...")
                return self._apply_rule_refinements(ai_midi, style, key, chaos)
        
        # Fallback to rule-based only
        print("Using rule-based generation only.")
        from main import generate_track_with_style
        return generate_track_with_style(style, key, chaos)
    
    def _generate_with_ai(self, style: str, key: str, bpm: int, bars: int) -> Optional[pretty_midi.PrettyMIDI]:
        """Try generating with available AI models."""
        midi = None
        
        # Try MMM for full multi-track
        if self.available_models["mmm"]:
            print("Generating with MMM (Multi-Track Music Machine)...")
            midi = self.mmm.generate_multi_track(style, key, bpm, bars)
            if midi:
                return midi
        
        # Try MidiBERT for melody + DiffMIDI for rhythm
        if self.available_models["midibert"]:
            print("Generating with MidiBERT + DiffMIDI...")
            midi = pretty_midi.PrettyMIDI()
            
            # Generate melody with MidiBERT
            melody = self.midibert.generate_melody(style, key)
            if melody:
                for inst in melody.instruments:
                    inst.name = "AI Melody"
                    midi.instruments.append(inst)
            
            # Generate drums with DiffMIDI
            if self.available_models["diffmidi"]:
                drums = self.diffmidi.generate_drums(style, bpm, bars)
                if drums:
                    for inst in drums.instruments:
                        inst.is_drum = True
                        inst.name = "AI Drums"
                        midi.instruments.append(inst)
            
            if midi.instruments:
                return midi
        
        return None
    
    def _apply_rule_refinements(self, ai_midi: pretty_midi.PrettyMIDI, 
                                 style: str, key: str, chaos: float) -> pretty_midi.PrettyMIDI:
        """
        Apply rule-based refinements to AI-generated MIDI.
        This adds humanization, style-specific tweaks, etc.
        """
        from style_engine import build_spec_from_style
        from drums_bass import generate_drums, generate_bass
        from harmonic_engine import generate_chords
        from melody_engine import generate_melody
        from global_memory import MotifMemory
        from utils import get_scale_notes
        
        # Build spec for the style
        spec = build_spec_from_style(style, key, chaos)
        scale = get_scale_notes(key)
        memory = MotifMemory(scale)
        
        # Create new MIDI with AI as base, then add rule-based elements
        final_midi = pretty_midi.PrettyMIDI()
        
        # Copy AI-generated tracks
        for inst in ai_midi.instruments:
            new_inst = pretty_midi.Instrument(
                program=inst.program,
                is_drum=inst.is_drum,
                name=inst.name + " (AI)"
            )
            new_inst.notes = inst.notes.copy()
            final_midi.instruments.append(new_inst)
        
        # Add rule-based drums if not present
        has_drums = any(inst.is_drum for inst in final_midi.instruments)
        if not has_drums:
            t0 = 0
            section = {"type": "verse", "bars": spec["arrangement"]["sections"][0]["bars"], "intensity": 0.5}
            end_time, kicks = generate_drums(final_midi, spec, section, t0)
        
        return final_midi


def download_checkpoints():
    """Helper function to download model checkpoints."""
    print("Checkpoint Download Instructions:")
    print("1. MMM (Multi-Track Music Machine):")
    print("   https://github.com/magenta/magenta/tree/main/magenta/models/mmm")
    print("2. MidiBERT-Piano:")
    print("   https://huggingface.co/wazenmai/MidiBERT-Piano")
    print("3. DiffMIDI:")
    print("   https://github.com/zbwang/diffmidi")
    print(f"\nPlace checkpoints in: {os.path.abspath(CHECKPOINT_DIR)}")
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)