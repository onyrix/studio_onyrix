import os

from ai.chords import encode_chords
from ai.config import DEFAULT_MODEL_PATH
from ai.tokenizer import MidiTokenizer
from ai.model import MidiTransformerModel
from ai.styles import encode_style


class MidiAIPipeline:
    def __init__(self, checkpoint_path=DEFAULT_MODEL_PATH):
        self.tokenizer = MidiTokenizer()
        self.model = MidiTransformerModel(checkpoint_path=checkpoint_path)

    def generate_from_midi(
        self,
        midi_path,
        out_path="output/generated.mid",
        style=None,
        chords=None,
        max_new_tokens=512
    ):
        tokens = self.tokenizer.encode_midi(midi_path)

        print("Encoding done")

        conditioning_tokens = []
        if style:
            conditioning_tokens.extend(encode_style(style))
        if chords:
            conditioning_tokens.extend(encode_chords(chords))

        generated = self.model.generate(
            conditioning_tokens + tokens,
            max_len=max_new_tokens
        )

        print("AI generation done")

        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        self.tokenizer.decode_tokens(generated, out_path)

        return out_path
