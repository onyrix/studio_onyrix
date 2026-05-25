import argparse

from generation.composer import generate_song
from generation.music_config import INSTRUMENT_LIBRARY, MOOD_LIBRARY, STYLE_LIBRARY
from generation.song_config import SongConfig


def parse_list(value):
    if not value:
        return []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a full multi-track MIDI song.")
    parser.add_argument("--title", default="Onyrix Song")
    parser.add_argument("--bpm", type=int, default=None)
    parser.add_argument("--mood", default="dreamy")
    parser.add_argument("--style", default="lofi", choices=sorted(STYLE_LIBRARY.keys()))
    parser.add_argument("--chords", default="Cmaj7,Am,F,G")
    parser.add_argument("--tracks", default="", help="Comma-separated instruments. Empty uses style defaults.")
    parser.add_argument("--bars", type=int, default=32)
    parser.add_argument("--prompt", default="")
    parser.add_argument("--output", default="output/generated_song.mid")
    parser.add_argument("--list-config", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.list_config:
        print("Styles:", ", ".join(sorted(STYLE_LIBRARY)))
        print("Moods:", ", ".join(sorted(MOOD_LIBRARY)))
        print("Instruments:", ", ".join(sorted(INSTRUMENT_LIBRARY)))
        return

    config = SongConfig(
        title=args.title,
        bpm=args.bpm,
        mood=args.mood,
        style=args.style,
        chords=parse_list(args.chords),
        tracks=parse_list(args.tracks),
        bars=args.bars,
        prompt=args.prompt,
        output=args.output,
    )

    out_path = generate_song(config)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
