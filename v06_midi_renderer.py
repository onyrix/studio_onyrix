"""
MIDI-only song renderer for Studio Onyrix v0.6.

This renderer generates deterministic DAW exports (project.json, master MIDI, per-track MIDI stems)
without any audio generation.
"""

from __future__ import annotations

import os
from typing import Dict

from daw_engine import DAWProject
from v06_renderer import OfflineSongRenderer


class MidiSongRenderer:
    """Render a complete song project with MIDI-only output."""

    def __init__(self):
        self.offline_renderer = OfflineSongRenderer()

    def render_project(self, project: DAWProject, output_dir: str) -> Dict[str, str]:
        """Render project to MIDI files only."""
        paths = self.offline_renderer.render_project(project, output_dir)
        
        # Update render settings to indicate MIDI-only mode
        project.render_settings["renderer"] = "midi_only"
        project.render_settings["master_audio_path"] = None
        project.render_settings["musicgen_audio_path"] = None
        
        # Save updated project
        project.save(paths["json"])
        
        return paths