from miditok import REMI, TokenizerConfig
from miditoolkit import MidiFile

class MidiTokenizer:
    def __init__(self):
        config = TokenizerConfig(
            use_programs=True,
            use_time_signatures=True
        )
        self.tokenizer = REMI(config)

    def encode_midi(self, midi_path):
        midi = MidiFile(midi_path)
        tokens = self.tokenizer(midi)
        return tokens

    def decode_tokens(self, tokens, out_path="out.mid"):
        midi = self.tokenizer.decode([tokens])[0]
        midi.dump(out_path)
        return out_path