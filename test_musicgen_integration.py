import json
import os
import unittest
import wave

from v06_musicgen_renderer import MidiSongRenderer  # Updated import
from v06_song_factory import create_song_project

RUN_MUSICGEN = os.environ.get("ONYRIX_RUN_MUSICGEN_TESTS") == "1"
MODEL_SIZE = os.environ.get("ONYRIX_MUSICGEN_MODEL", "large")
DURATION = int(os.environ.get("ONYRIX_MUSICGEN_DURATION", "4"))

@unittest.skipUnless(RUN_MUSICGEN, "set ONYRIX_RUN_MUSICGEN_TESTS=1 to run MusicGen integration")
class MusicGenIntegrationTests(unittest.TestCase):
    def test_midi_generation_project(self):
        project = create_song_project(
            style="synthwave",
            name=f"MIDI {MODEL_SIZE} Smoke",
            measures=8,
        )
        renderer = MidiSongRenderer()
        self.assertTrue(renderer.available, "MIDI renderer is not available")

        output_dir = os.path.join("output", "midi_tests", MODEL_SIZE)
        paths = renderer.render_project(project, output_dir, duration=DURATION)

        for key in ("json", "midi", "midi_drums", "midi_bass", "midi_chords", "midi_lead"):
            self.assertIn(key, paths)
            self.assertTrue(os.path.exists(paths[key]), paths[key])
            self.assertGreater(os.path.getsize(paths[key]), 64, paths[key])

        with open(paths["json"], "r") as f:
            data = json.load(f)
            self.assertEqual(data["schema_version"], "0.6")
            self.assertEqual(data["render_settings"]["renderer"], "midi_only")
            self.assertIn("MIDI", data["memory"]["generation_history"][-1]["generator"])

        # No WAV checks needed for MIDI-only workflow
        # with wave.open(paths["wav"], "rb") as wav:
        #     self.assertGreater(wav.getnframes(), 0)
        #     self.assertIn(wav.getnchannels(), (1, 2))

if __name__ == "__main__":
    unittest.main()