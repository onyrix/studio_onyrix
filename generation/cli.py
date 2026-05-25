import argparse

from ai.config import DEFAULT_MODEL_PATH
from ai.pipeline import GenerationJob, MidiAIPipeline


def parse_chords(value):
    if not value:
        return []

    return [
        chord.strip()
        for chord in value.split(",")
        if chord.strip()
    ]


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a MIDI continuation.")
    parser.add_argument("--input", default="input.mid", help="Seed MIDI file.")
    parser.add_argument("--output", default="output/generated.mid", help="Output MIDI file.")
    parser.add_argument("--style", default=None, help="Style token name, e.g. LOFI or JAZZ.")
    parser.add_argument("--chords", default="", help="Comma-separated chord list, e.g. Cmaj7,Am,F,G.")
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--checkpoint", default=DEFAULT_MODEL_PATH)
    return parser.parse_args()


def main():
    args = parse_args()
    pipeline = MidiAIPipeline(checkpoint_path=args.checkpoint)
    job = GenerationJob(
        midi_path=args.input,
        out_path=args.output,
        style=args.style,
        chords=parse_chords(args.chords),
        max_new_tokens=args.max_new_tokens,
    )

    out_path = pipeline.generate_job(job)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
