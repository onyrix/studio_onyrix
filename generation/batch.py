import argparse
from pathlib import Path

from generation.composer import generate_song
from generation.song_config import SongConfig


PRESETS = [
    {
        "title": "Neon Rain",
        "style": "lofi",
        "mood": "dreamy",
        "bpm": 78,
        "chords": ["Cmaj7", "Am7", "Fmaj7", "G"],
        "prompt": "warm vinyl keys, late night rain, human loose timing",
    },
    {
        "title": "Blue Room Session",
        "style": "jazz",
        "mood": "romantic",
        "bpm": 116,
        "chords": ["Dm7", "G7", "Cmaj7", "Am7"],
        "prompt": "small club quartet, elegant lead, brushed groove",
    },
    {
        "title": "Ashes Over Orion",
        "style": "cinematic",
        "mood": "epic",
        "bpm": 92,
        "chords": ["Am", "F", "C", "G"],
        "prompt": "wide strings, heroic piano, dark trailer pulse",
    },
    {
        "title": "Glass Garden",
        "style": "ambient",
        "mood": "dreamy",
        "bpm": 68,
        "chords": ["Fmaj7", "Cmaj7", "G", "Am"],
        "prompt": "floating pads, sparse piano, soft evolving melody",
    },
    {
        "title": "Voltage Smile",
        "style": "edm",
        "mood": "energetic",
        "bpm": 128,
        "chords": ["C", "G", "Am", "F"],
        "prompt": "festival plucks, bright hook, four on the floor",
    },
    {
        "title": "Chrome Avenue",
        "style": "synthwave",
        "mood": "dark",
        "bpm": 100,
        "chords": ["Am", "F", "Dm", "E"],
        "prompt": "retro night drive, analog bass, melancholic neon lead",
    },
]


def slugify(value):
    chars = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "_":
            chars.append("_")

    return "".join(chars).strip("_") or "song"


def parse_args():
    parser = argparse.ArgumentParser(description="Generate several full MIDI songs.")
    parser.add_argument("--output-dir", default="output/generated_songs")
    parser.add_argument("--bars", type=int, default=32)
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for preset in PRESETS:
        config = SongConfig(
            title=preset["title"],
            bpm=preset["bpm"],
            mood=preset["mood"],
            style=preset["style"],
            chords=preset["chords"],
            bars=args.bars,
            prompt=preset["prompt"],
            output=str(output_dir / f"{slugify(preset['title'])}.mid"),
        )
        out_path = generate_song(config)
        print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
