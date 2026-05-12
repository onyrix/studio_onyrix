import json
import os
import unittest
import wave

from daw_engine import DAWPart, DAWProject
from v05_renderer import OfflineSongRenderer


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
    project = DAWProject(
        name=config["name"],
        bpm=config["bpm"],
        root=config["root"],
        scale=config["scale"],
        chord_progression=config["chords"],
        groove=config["groove"],
        swing=config["swing"],
        style_tags=config["style"],
        description=f"v0.5 export test fixture for {config['name']}",
    )

    project.find_track("bass").pan = -0.10
    project.find_track("chords").pan = 0.12
    project.find_track("lead").pan = 0.20

    slug = config["slug"]
    common = {
        "bpm": project.bpm,
        "root": project.root,
        "scale": project.scale,
    }
    project.add_part(DAWPart(
        **common,
        id=f"{slug}_drums",
        instrument="trap_drums" if config["groove"] == "trap" else "drums_full",
        instrument_class="drums",
        track_id="drums",
        start_bar=1,
        measures=8,
        relation="verse",
        extra_prompt=f"{config['groove']} drums",
    ))
    project.add_part(DAWPart(
        **common,
        id=f"{slug}_bass",
        instrument="808_bass" if config["groove"] == "trap" else "synth_bass",
        instrument_class="bass",
        track_id="bass",
        start_bar=1,
        measures=8,
        relation="verse",
        extra_prompt="follow chord roots tightly",
    ))
    project.add_part(DAWPart(
        **common,
        id=f"{slug}_chords",
        instrument="synth_pad" if config["groove"] != "rock" else "piano",
        instrument_class="chords",
        track_id="chords",
        start_bar=1,
        measures=8,
        relation="verse",
        extra_prompt="clear harmonic bed",
    ))
    project.add_part(DAWPart(
        **common,
        id=f"{slug}_lead",
        instrument="synth_lead" if config["groove"] != "rock" else "guitar_melody",
        instrument_class="lead",
        track_id="lead",
        start_bar=5,
        measures=4,
        relation="chorus",
        extra_prompt="short memorable hook",
    ))
    return project


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
                    self.assertGreater(os.path.getsize(path), 128, path)

                with open(paths["json"], "r") as f:
                    data = json.load(f)
                self.assertEqual(data["schema_version"], "0.5")
                self.assertEqual(data["transport"]["bpm"], config["bpm"])
                self.assertEqual(data["musical_context"]["groove"], config["groove"])
                self.assertEqual(len(data["tracks"]), 5)
                self.assertEqual(len(data["parts"]), 4)
                self.assertGreaterEqual(len(data["assets"]["audio"]), 4)
                self.assertGreaterEqual(len(data["assets"]["midi"]), 4)
                self.assertEqual(len(data["memory"]["generation_history"]), 4)

                with open(paths["midi"], "rb") as f:
                    self.assertEqual(f.read(4), b"MThd")

                with wave.open(paths["wav"], "rb") as wav:
                    self.assertEqual(wav.getnchannels(), 2)
                    self.assertEqual(wav.getframerate(), 32000)
                    self.assertGreater(wav.getnframes(), 32000)


if __name__ == "__main__":
    unittest.main()
