import os
from numbers import Integral

from miditok import REMI, TokenizerConfig
from miditoolkit import MidiFile


class MidiTokenizer:
    def __init__(self):
        config = TokenizerConfig(
            use_programs=True,
            use_tempos=True,
            use_time_signatures=True
        )
        self.tokenizer = REMI(config)
        self.base_vocab_size = len(self.tokenizer)

    def encode_midi(self, midi_path):
        midi = MidiFile(midi_path)
        tokens = self.tokenizer(midi)
        return tokens.ids

    def decode_tokens(self, tokens, out_path="out.mid"):
        midi_tokens = [
            int(token)
            for token in tokens
            if isinstance(token, Integral) and 0 <= token < self.base_vocab_size
        ]

        if not midi_tokens:
            raise ValueError("No valid MIDI tokenizer tokens to decode.")

        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        midi = self.tokenizer.decode(midi_tokens)
        if isinstance(midi, list):
            midi = midi[0]

        if hasattr(midi, "dump_midi"):
            midi.dump_midi(out_path)
        else:
            midi.dump(out_path)

        return out_path
