"""
MusicGen song renderer for Studio Onyrix v0.6.

This renderer keeps the deterministic DAW exports from v06_renderer
(`project.json`, master MIDI, per-track MIDI stems) and adds a MusicGen master
WAV generated from the full project context.
"""

from __future__ import annotations

import os
from typing import Dict, Optional

import numpy as np

from daw_engine import DAWProject
from modern_ai_generator import MusicGenGenerator
from v06_renderer import OfflineSongRenderer

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False


class MusicGenSongRenderer:
    """Render a complete song project with MusicGen as the master audio layer."""

    def __init__(self, model_size: str = "large", device: Optional[str] = None,
                 offline_renderer: Optional[OfflineSongRenderer] = None):
        self.model_size = model_size
        self.device = device
        self.offline_renderer = offline_renderer or OfflineSongRenderer()
        self.generator = MusicGenGenerator(model_size=model_size, device=device)

    @property
    def available(self) -> bool:
        return bool(self.generator.available and SOUNDFILE_AVAILABLE)

    def render_project(self, project: DAWProject, output_dir: str,
                       duration: Optional[int] = None) -> Dict[str, str]:
        paths = self.offline_renderer.render_project(project, output_dir)
        if not self.available:
            raise RuntimeError("MusicGen is not available. Install torch, torchaudio, transformers and soundfile.")

        prompt = self.build_song_prompt(project)
        render_duration = duration or max(4, min(int(project.total_duration), 95))
        audio = self.generator.generate(
            prompt=prompt,
            duration=render_duration,
            temperature=0.95,
            top_k=250,
            cfg_coef=3.5,
        )
        if audio is None:
            raise RuntimeError("MusicGen returned no audio.")

        wav_path = os.path.join(output_dir, "musicgen_master.wav")
        self._save_audio(audio, wav_path)

        project.render_settings["musicgen_model"] = self.model_size
        project.render_settings["musicgen_prompt"] = prompt
        project.render_settings["musicgen_audio_path"] = wav_path
        project.render_settings["master_audio_path"] = wav_path
        project.memory.setdefault("generation_history", []).append({
            "generator": "MusicGen",
            "model": self.model_size,
            "prompt": prompt,
            "audio_path": wav_path,
            "duration_seconds": render_duration,
        })
        project.save(paths["json"])
        paths["musicgen_wav"] = wav_path
        paths["wav"] = wav_path
        return paths

    def build_song_prompt(self, project: DAWProject) -> str:
        sections = project.memory.get("arrangement", []) if isinstance(project.memory, dict) else []
        section_text = ", ".join(
            f"{s.get('type')} {s.get('bars')} bars energy {s.get('energy')}"
            for s in sections
        )
        instruments = []
        for track in project.tracks:
            part_instruments = sorted({p.instrument for p in project.parts if p.track_id == track.id})
            if part_instruments:
                instruments.append(f"{track.name}: {', '.join(part_instruments)}")

        return (
            f"Complete professional {', '.join(project.style_tags) or project.groove} song. "
            f"{project.generation_context()} "
            f"Arrangement: {section_text}. "
            f"Tracks and instruments: {'; '.join(instruments)}. "
            "Produce a cohesive full mix with clear drums, bass, harmony, lead hook, and transitions. "
            "No vocals unless explicitly implied by the style."
        )

    def _save_audio(self, audio: np.ndarray, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if audio.ndim == 2:
            audio_for_sf = audio.T if audio.shape[0] <= 2 else audio
        else:
            audio_for_sf = audio
        sf.write(filepath, audio_for_sf, getattr(self.generator, "sample_rate", 32000))
