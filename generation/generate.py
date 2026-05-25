from ai.pipeline import MidiAIPipeline


def main():
    pipeline = MidiAIPipeline()
    out_path = pipeline.generate_from_midi(
        "input.mid",
        out_path="output/generated_chord.mid",
        style="LOFI",
        chords=["Cmaj7", "Am", "F", "G"],
    )

    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
