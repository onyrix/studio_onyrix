from ai.tokenizer import MidiTokenizer
from ai.model import MidiTransformerModel

class MidiAIPipeline:
    def __init__(self):
        self.tokenizer = MidiTokenizer()
        self.model = MidiTransformerModel()

    def generate_from_midi(self, midi_path):
        tokens = self.tokenizer.encode_midi(midi_path)

        print("🎹 Encoding done")

        generated = self.model.generate(tokens, max_len=512)

        print("🧠 AI generation done")

        out_path = "output/generated.mid"
        self.tokenizer.decode_tokens(generated, out_path)

        return out_path