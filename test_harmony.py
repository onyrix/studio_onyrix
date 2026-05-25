import unittest

from ai.harmony import extract_chord_timeline, extract_chords


class HarmonyTests(unittest.TestCase):
    def test_extract_chords_returns_list(self):
        chords = extract_chords("input.mid")

        self.assertIsInstance(chords, list)

    def test_extract_chord_timeline_returns_timed_items(self):
        timeline = extract_chord_timeline("input.mid")

        self.assertIsInstance(timeline, list)
        for item in timeline:
            self.assertIn("time", item)
            self.assertIn("chord", item)


if __name__ == "__main__":
    unittest.main()
