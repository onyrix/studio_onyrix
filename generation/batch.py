import argparse
from pathlib import Path

from ai.config import DEFAULT_MODEL_PATH
from ai.pipeline import GenerationJob, MidiAIPipeline


PRESETS = [
    {
        "name": "lofi_calm",
        "style": "LOFI",
        "chords": ["Cmaj7", "Am", "F", "G"],
    },
    {
        "name": "jazz_minor",
        "style": "JAZZ",
        "chords": ["Dm7", "G7", "Cmaj7", "Am7"],
    },
    {
        "name": "cinematic_dark",
        "style": "CINEMATIC",
        "chords": ["Am", "F", "C", "G"],
    },
    {
        "name": "ambient_open",
        "style": "AMBIENT",
        "chords": ["Fmaj7", "Cmaj7", "G", "Am"],
    },
    {
        "name": "edm_bright",
        "style": "EDM",
        "chords": ["C", "G", "Am", "F"],
    },
]


def build_jobs(input_path, output_dir, max_new_tokens):
    output_dir = Path(output_dir)

    for preset in PRESETS:
        yield GenerationJob(
            midi_path=input_path,
            out_path=str(output_dir / f"{preset['name']}.mid"),
            style=preset["style"],
            chords=preset["chords"],
            max_new_tokens=max_new_tokens,
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Generate several MIDI variations.")
    parser.add_argument("--input", default="input.mid", help="Seed MIDI file.")
    parser.add_argument("--output-dir", default="output/generated_variations")
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--checkpoint", default=DEFAULT_MODEL_PATH)
    return parser.parse_args()


def main():
    args = parse_args()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    pipeline = MidiAIPipeline(checkpoint_path=args.checkpoint)

    for job in build_jobs(args.input, args.output_dir, args.max_new_tokens):
        out_path = pipeline.generate_job(job)
        print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
