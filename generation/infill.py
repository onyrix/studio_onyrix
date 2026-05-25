from ai.config import DEFAULT_MODEL_PATH
from ai.model import MidiTransformerModel
from ai.tokenizer import MidiTokenizer


def infill(tokens, model=None, start=128, length=128):
    model = model or MidiTransformerModel(checkpoint_path=DEFAULT_MODEL_PATH)
    prefix = tokens[:start]
    generated = model.generate(prefix, max_len=length)

    return prefix + generated[len(prefix):] + tokens[start + length:]


def main():
    tokenizer = MidiTokenizer()
    tokens = tokenizer.encode_midi("input.mid")

    print("MIDI loaded")

    out = infill(tokens)

    print("Infill complete")

    out_path = tokenizer.decode_tokens(out, "output/infilled.mid")

    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
