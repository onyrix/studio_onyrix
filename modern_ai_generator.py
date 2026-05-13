"""
Modern AI Generator - State-of-the-Art Music Generation

This module uses Meta's MusicGen model via HuggingFace transformers
for state-of-the-art music generation. Generates professional-quality 
audio directly from text descriptions, with zero cloud costs.
"""

import numpy as np
import os
from typing import Optional, Dict, List

# Check available modern AI libraries
try:
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    MUSICGEN_AVAILABLE = True
except ImportError:
    torch = None
    MUSICGEN_AVAILABLE = False
    print("Warning: MusicGen dependencies not available.")
    print("Install: pip install torch torchaudio transformers")

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Warning: librosa not available. Audio analysis disabled.")
    print("Install: pip install librosa")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("Warning: soundfile not available.")


class MusicGenGenerator:
    """
    Primary AI generator using Meta's MusicGen (state-of-the-art).
    
    MusicGen is trained on 20,000+ hours of music and generates
    high-quality audio directly from text descriptions.
    """
    
    def __init__(self, model_size: str = 'large', device: Optional[str] = None):
        """
        Initialize MusicGen generator.
        
        Args:
            model_size: 'small' (300MB), 'medium' (1.5GB), 'large' (3GB)
            device: 'cuda' or 'cpu' (auto-detects GPU if available)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_size = model_size
        self.model = None
        self.processor = None
        self.available = False
        self.sample_rate = 32000
        
        if MUSICGEN_AVAILABLE:
            try:
                print(f"\nLoading MusicGen-{model_size} on {self.device}...")
                
                model_name = f"facebook/musicgen-{model_size}"
                self.processor = AutoProcessor.from_pretrained(model_name)
                self.model = MusicgenForConditionalGeneration.from_pretrained(model_name)
                self.model.to(self.device)
                self.sample_rate = getattr(self.model.config.audio_encoder, "sampling_rate", 32000)
                
                self.available = True
                print(f"MusicGen-{model_size} loaded successfully.")
                print(f"  Device: {self.device}")
                print(f"  Sample rate: {self.sample_rate} Hz")
                print(f"  Max duration: {30 if model_size == 'small' else 95} seconds")
            except Exception as e:
                print(f"Failed to load MusicGen: {e}")
                print("  Try: pip install torch torchaudio transformers")
                print("  Or use model_size='small' for lower memory")
        else:
            print("MusicGen not available. Install: pip install transformers")
    
    def generate(self, 
                prompt: str, 
                duration: int = 30,
                top_k: int = 250,
                top_p: float = 0.0,
                temperature: float = 1.0,
                cfg_coef: float = 3.0) -> Optional[np.ndarray]:
        """
        Generate high-quality audio from text prompt.
        
        Args:
            prompt: Text description (e.g., "agressive trap beat with heavy 808s")
            duration: Length in seconds (30 for small, 95 for medium/large)
            top_k: Number of top tokens to consider (higher = more variety)
            top_p: Nucleus sampling threshold (0.0 = disabled)
            temperature: Sampling temperature (1.0 = normal, 0.5 = more focused)
            cfg_coef: Classifier-free guidance coefficient (higher = follows prompt more)
        
        Returns:
            NumPy array of audio samples at 32kHz, or None if failed
        """
        if not self.available or not self.model:
            print("MusicGen not available.")
            return None
        
        max_duration = 30 if self.model_size == 'small' else 95
        duration = min(duration, max_duration)
        
        try:
            gen_kwargs = {
                "max_new_tokens": int(duration * 50),
                "do_sample": True,
                "top_k": top_k,
                "top_p": top_p if top_p > 0 else None,
                "temperature": temperature,
                "guidance_scale": cfg_coef,
            }
            gen_kwargs = {k: v for k, v in gen_kwargs.items() if v is not None}
            
            print(f"\nGenerating with MusicGen...")
            print(f"  Prompt: '{prompt}'")
            print(f"  Duration: {duration}s")
            print(f"  Device: {self.device}")
            
            inputs = self.processor(
                text=[prompt],
                padding=True,
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                audio_values = self.model.generate(**inputs, **gen_kwargs)
            
            # transformers v5 returns audio tensor directly
            if hasattr(audio_values, 'audio_values'):
                audio = audio_values.audio_values.cpu().numpy()
            else:
                audio = audio_values.cpu().numpy()
            
            if audio.ndim == 3:
                audio = audio[0]
            
            print(f"Generated audio: {audio.shape}")
            return audio
            
        except Exception as e:
            print(f"MusicGen generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None


class AudioAnalyzer:
    """
    Analyze AI-generated audio to extract musical information.
    Useful for DAW integration and granular control.
    """
    
    def __init__(self):
        self.available = LIBROSA_AVAILABLE
        if not self.available:
            print("Audio analysis disabled. Install: pip install librosa")
    
    def analyze(self, audio: np.ndarray, sr: int = 32000) -> Dict:
        """
        Extract musical features from audio.
        
        Args:
            audio: Audio array (channels, samples) or (samples,)
            sr: Sample rate (MusicGen outputs at 32kHz)
        
        Returns:
            Dict with: tempo, beat_times, pitches, duration, etc.
        """
        if not self.available:
            return {}
        
        result = {}
        
        if audio.ndim == 2:
            y = np.mean(audio, axis=0)
        else:
            y = audio
        
        try:
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            result['tempo'] = float(tempo)
            result['beat_times'] = librosa.frames_to_time(beat_frames, sr=sr).tolist()
            result['num_beats'] = len(beat_frames)
            
            result['duration'] = len(y) / sr
            
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            result['pitch_mean'] = float(np.mean(pitches[pitches > 0])) if np.any(pitches > 0) else 0
            
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            result['spectral_centroid_mean'] = float(np.mean(spectral_centroid))
            
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            result['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
            
            print(f"\nAudio Analysis:")
            print(f"  Tempo: {result['tempo']:.1f} BPM")
            print(f"  Duration: {result['duration']:.1f}s")
            print(f"  Beats: {result['num_beats']}")
            print(f"  Pitch (mean): {result['pitch_mean']:.1f} Hz")
            
        except Exception as e:
            print(f"Audio analysis failed: {e}")
            result['error'] = str(e)
        
        return result


class ModernAIPipeline:
    """
    Unified pipeline: Modern AI generation + DAW-ready outputs.
    
    Replaces the weak HybridMIDIGenerator from v2.
    """
    
    def __init__(self, model_size: str = 'large'):
        self.musicgen = MusicGenGenerator(model_size=model_size)
        self.analyzer = AudioAnalyzer()
        
        print(f"\n{'='*60}")
        print("Modern AI Pipeline Status:")
        print(f"  MusicGen: {'OK' if self.musicgen.available else 'MISSING'}")
        print(f"  Audio Analysis: {'OK' if self.analyzer.available else 'MISSING'}")
        print(f"{'='*60}\n")
    
    def generate_track(self,
                          prompt: str,
                          duration: int = 30,
                          analyze: bool = True,
                          output_dir: str = "output") -> Dict:
        """
        Generate a complete track using modern AI.
        
        Args:
            prompt: Text description
            duration: Length in seconds
            analyze: Whether to analyze the audio for DAW integration
            output_dir: Where to save outputs
        
        Returns:
            Dict with: 'audio', 'analysis', 'paths', 'metadata'
        """
        result = {
            'audio': None,
            'analysis': {},
            'paths': {},
            'metadata': {
                'prompt': prompt,
                'duration': duration,
                'generator': 'MusicGen',
                'model_size': self.musicgen.model_size
            }
        }
        
        audio = self.musicgen.generate(prompt, duration)
        
        if audio is None:
            print("Generation failed.")
            return result
        
        result['audio'] = audio
        
        if analyze and self.analyzer.available:
            result['analysis'] = self.analyzer.analyze(audio)
        
        result['paths'] = self._save_outputs(audio, prompt, output_dir)
        
        return result
    
    def _save_outputs(self, audio: np.ndarray, prompt: str, output_dir: str) -> Dict:
        """Save audio and metadata to files."""
        import os
        from datetime import datetime
        
        os.makedirs(output_dir, exist_ok=True)
        
        paths = {}
        
        safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_prompt = safe_prompt.replace(' ', '_')[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{safe_prompt}_{timestamp}"
        
        if SOUNDFILE_AVAILABLE:
            wav_path = os.path.join(output_dir, f"{base_name}.wav")
            try:
                if audio.ndim == 2:
                    audio_for_sf = audio.T if audio.shape[0] <= 2 else audio
                else:
                    audio_for_sf = audio
                
                sf.write(wav_path, audio_for_sf, 32000)
                paths['wav'] = wav_path
                print(f"Audio saved: {wav_path}")
            except Exception as e:
                print(f"Failed to save WAV: {e}")
        
        json_path = os.path.join(output_dir, f"{base_name}.json")
        try:
            import json
            metadata = {
                'prompt': prompt,
                'duration': audio.shape[-1] / 32000,
                'sample_rate': 32000,
                'model': self.musicgen.model_size,
                'timestamp': timestamp
            }
            with open(json_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            paths['json'] = json_path
        except Exception as e:
            print(f"Failed to save metadata: {e}")
        
        return paths
