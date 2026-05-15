import os
from ai.pipeline import MidiAIPipeline

OUTPUT_DIR = "output"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pipeline = MidiAIPipeline()

    input_midi = "input.mid"  # metti un file MIDI reale qui

    print("🚀 Running AI MIDI generation...")

    out = pipeline.generate_from_midi(input_midi)

    print(f"✔ Generated: {out}")

if __name__ == "__main__":
    main()