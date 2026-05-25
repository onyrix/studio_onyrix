import os
import unittest

from ai.pipeline import MidiAIPipeline
from ai.tokenizer import MidiTokenizer


class EchoModel:
    def generate(self, input_ids, max_len=512):
        return input_ids


class GenerateMidiTests(unittest.TestCase):
    def test_pipeline_generates_decodable_midi(self):
        pipeline = MidiAIPipeline.__new__(MidiAIPipeline)
        pipeline.tokenizer = MidiTokenizer()
        pipeline.model = EchoModel()

        out_path = "output/test_generated.mid"
        result = pipeline.generate_from_midi("input.mid", out_path=out_path)

        self.assertEqual(result, out_path)
        self.assertTrue(os.path.exists(out_path))
        self.assertGreater(os.path.getsize(out_path), 0)


if __name__ == "__main__":
    unittest.main()
