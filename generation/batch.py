import argparse
from pathlib import Path

from generation.composer import generate_song
from generation.music_config import MOOD_LIBRARY, STYLE_LIBRARY
from generation.project import PROJECT_NAME, PROJECT_VERSION
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
    {
        "title": "Velvet Afterparty",
        "style": "rnb",
        "mood": "luxury",
        "bpm": 92,
        "chords": ["Cm9", "Abmaj7", "Ebmaj7", "G7"],
        "prompt": "silky keys, intimate vocal-like lead, late night groove",
    },
    {
        "title": "Pacific Motion",
        "style": "house",
        "mood": "euphoric",
        "bpm": 124,
        "chords": ["Am7", "Fmaj7", "Cmaj7", "G"],
        "prompt": "bright dance club pulse, uplifting piano hook",
    },
    {
        "title": "Static Jungle",
        "style": "drum_and_bass",
        "mood": "tense",
        "bpm": 172,
        "chords": ["Fm", "Ab", "Eb", "Db"],
        "prompt": "dense breakbeat pressure, dark bass movement",
    },
    {
        "title": "Salt And Brass",
        "style": "latin",
        "mood": "playful",
        "bpm": 104,
        "chords": ["Am", "Dm", "E7", "Am"],
        "prompt": "syncopated latin groove, brass stabs, live human timing",
    },
]


def parse_list(value):
    if not value:
        return []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def slugify(value):
    chars = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "_":
            chars.append("_")

    return "".join(chars).strip("_") or "song"


def build_style_jobs(styles, moods, bars, output_dir, prompt_suffix):
    for style in styles:
        style_config = STYLE_LIBRARY[style]
        for mood in moods:
            title = f"{style.replace('_', ' ').title()} {mood.title()}"
            prompt = (
                f"{style} song with {mood} mood, complete multitrack arrangement"
            )
            if prompt_suffix:
                prompt = f"{prompt}, {prompt_suffix}"

            yield SongConfig(
                title=title,
                bpm=style_config["bpm"],
                mood=mood,
                style=style,
                chords=list(style_config["chords"]),
                bars=bars,
                prompt=prompt,
                output=str(output_dir / f"{slugify(title)}.mid"),
            )


def build_preset_jobs(bars, output_dir, prompt_suffix):
    for preset in PRESETS:
        prompt = preset["prompt"]
        if prompt_suffix:
            prompt = f"{prompt}, {prompt_suffix}"

        yield SongConfig(
            title=preset["title"],
            bpm=preset["bpm"],
            mood=preset["mood"],
            style=preset["style"],
            chords=preset["chords"],
            bars=bars,
            prompt=prompt,
            output=str(output_dir / f"{slugify(preset['title'])}.mid"),
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Generate batches of full MIDI songs.")
    parser.add_argument("--version", action="version", version=f"{PROJECT_NAME} {PROJECT_VERSION}")
    parser.add_argument("--output-dir", default="output/generated_songs")
    parser.add_argument("--bars", type=int, default=32)
    parser.add_argument(
        "--mode",
        choices=("presets", "styles", "all"),
        default="presets",
        help="presets uses curated songs, styles creates a style/mood matrix, all does both.",
    )
    parser.add_argument(
        "--styles",
        default="",
        help="Comma-separated styles for --mode styles/all. Empty means all styles.",
    )
    parser.add_argument(
        "--moods",
        default="",
        help="Comma-separated moods for --mode styles/all. Empty means dreamy,energetic,dark,peaceful.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Maximum songs to generate. 0 means no limit.")
    parser.add_argument("--prompt-suffix", default="", help="Text appended to every generated prompt.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned songs without writing MIDI files.")
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    selected_styles = parse_list(args.styles) or sorted(STYLE_LIBRARY)
    selected_moods = parse_list(args.moods) or ["dreamy", "energetic", "dark", "peaceful"]

    unknown_styles = [style for style in selected_styles if style not in STYLE_LIBRARY]
    unknown_moods = [mood for mood in selected_moods if mood not in MOOD_LIBRARY]
    if unknown_styles:
        raise ValueError(f"Unknown styles: {', '.join(unknown_styles)}")
    if unknown_moods:
        raise ValueError(f"Unknown moods: {', '.join(unknown_moods)}")

    jobs = []
    if args.mode in ("presets", "all"):
        jobs.extend(build_preset_jobs(args.bars, output_dir, args.prompt_suffix))
    if args.mode in ("styles", "all"):
        jobs.extend(build_style_jobs(selected_styles, selected_moods, args.bars, output_dir, args.prompt_suffix))

    if args.limit > 0:
        jobs = jobs[:args.limit]

    print(f"{PROJECT_NAME} {PROJECT_VERSION} batch: {len(jobs)} song(s)")
    for config in jobs:
        if args.dry_run:
            print(f"Would generate {config.title} -> {config.output}")
            continue

        out_path = generate_song(config)
        print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
