import os
import unittest

from miditoolkit import MidiFile

from generation.composer import generate_song
from generation.music_config import INSTRUMENT_LIBRARY, MOOD_LIBRARY, STYLE_LIBRARY
from generation.project import PROJECT_VERSION
from generation.song_config import SongConfig


class GenerateMidiTests(unittest.TestCase):
    def test_music_configuration_is_available(self):
        self.assertEqual(PROJECT_VERSION, "0.70")
        self.assertIn("synthwave", STYLE_LIBRARY)
        self.assertIn("drum_and_bass", STYLE_LIBRARY)
        self.assertIn("minimal_piano", STYLE_LIBRARY)
        self.assertIn("peaceful", MOOD_LIBRARY)
        self.assertIn("euphoric", MOOD_LIBRARY)
        self.assertIn("bell", INSTRUMENT_LIBRARY)
        self.assertIn("harp", INSTRUMENT_LIBRARY)
        self.assertIn("tracks", STYLE_LIBRARY["lofi"])

    def test_full_song_generator_creates_multitrack_midi(self):
        out_path = "output/test_full_song.mid"
        result = generate_song(
            SongConfig(
                title="Unit Test Groove",
                bpm=96,
                mood="dreamy",
                style="lofi",
                chords=["Cmaj7", "Am7", "Fmaj7", "G"],
                bars=8,
                prompt="human cool laidback keys",
                output=out_path,
            )
        )

        midi = MidiFile(result)

        self.assertEqual(result, out_path)
        self.assertTrue(os.path.exists(out_path))
        self.assertGreaterEqual(len(midi.instruments), 4)
        self.assertTrue(any(instrument.is_drum for instrument in midi.instruments))
        self.assertGreater(sum(len(instrument.notes) for instrument in midi.instruments), 40)


if __name__ == "__main__":
    unittest.main()
