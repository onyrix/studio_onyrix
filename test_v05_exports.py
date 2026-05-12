import json
import os
import unittest
import wave

from v05_renderer import OfflineSongRenderer
from v05_song_factory import create_song_project


OUTPUT_ROOT = os.path.join("output", "v05_test_songs")


SONG_FIXTURES = [
    {
        "slug": "trap_noir",
        "name": "Trap Noir",
        "bpm": 140,
        "root": "A",
        "scale": "natural_minor",
        "chords": ["Am", "F", "C", "G"],
        "groove": "trap",
        "swing": 0.10,
        "style": ["trap", "dark", "club"],
    },
    {
        "slug": "neon_synthwave",
        "name": "Neon Synthwave",
        "bpm": 100,
        "root": "D",
        "scale": "natural_minor",
        "chords": ["Dm", "Bb", "F", "C"],
        "groove": "synthwave",
        "swing": 0.0,
        "style": ["synthwave", "retro", "cinematic"],
    },
    {
        "slug": "lofi_sunset",
        "name": "Lofi Sunset",
        "bpm": 78,
        "root": "C",
        "scale": "major",
        "chords": ["Cmaj7", "Am", "Fmaj7", "G"],
        "groove": "lofi",
        "swing": 0.18,
        "style": ["lofi", "warm", "chill"],
    },
    {
        "slug": "garage_rock",
        "name": "Garage Rock",
        "bpm": 126,
        "root": "E",
        "scale": "minor_pentatonic",
        "chords": ["Em", "G", "D", "A"],
        "groove": "rock",
        "swing": 0.0,
        "style": ["rock", "garage", "live"],
    },
]


def build_project(config):
    style = {
        "trap_noir": "trap",
        "neon_synthwave": "synthwave",
        "lofi_sunset": "lofi",
        "garage_rock": "rock",
    }[config["slug"]]
    return create_song_project(
        style=style,
        name=config["name"],
        bpm=config["bpm"],
        root=config["root"],
        scale=config["scale"],
        chords=config["chords"],
        measures=24,
    )


class V05ExportTests(unittest.TestCase):
    def test_four_genre_projects_export_json_midi_wav(self):
        renderer = OfflineSongRenderer(sample_rate=32000)

        for config in SONG_FIXTURES:
            with self.subTest(genre=config["slug"]):
                project = build_project(config)
                output_dir = os.path.join(OUTPUT_ROOT, config["slug"])
                paths = renderer.render_project(project, output_dir)

                for path in paths.values():
                    self.assertTrue(os.path.exists(path), path)
                    min_size = 64 if path.endswith(".mid") else 128
                    self.assertGreater(os.path.getsize(path), min_size, path)

                with open(paths["json"], "r") as f:
                    data = json.load(f)
                self.assertEqual(data["schema_version"], "0.5")
                self.assertEqual(data["transport"]["bpm"], config["bpm"])
                self.assertEqual(data["musical_context"]["groove"], config["groove"])
                self.assertEqual(len(data["tracks"]), 5)
                self.assertGreaterEqual(len(data["parts"]), 8)
                self.assertEqual(len(data["assets"]["audio"]), 1)
                self.assertEqual(data["assets"]["audio"][0]["scope"], "master")
                self.assertGreaterEqual(len(data["assets"]["midi"]), 5)
                self.assertEqual(len(data["memory"]["generation_history"]), len(data["parts"]))

                with open(paths["midi"], "rb") as f:
                    self.assertEqual(f.read(4), b"MThd")
                for track_id in ("drums", "bass", "chords", "lead"):
                    with open(paths[f"midi_{track_id}"], "rb") as f:
                        self.assertEqual(f.read(4), b"MThd")

                with wave.open(paths["wav"], "rb") as wav:
                    self.assertEqual(wav.getnchannels(), 2)
                    self.assertEqual(wav.getframerate(), 32000)
                    self.assertGreater(wav.getnframes(), 32000)


if __name__ == "__main__":
    unittest.main()
