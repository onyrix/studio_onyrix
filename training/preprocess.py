import os
import json
from pathlib import Path

from miditok import REMI, TokenizerConfig
from miditoolkit import MidiFile

from ai.harmony import extract_chord_timeline
from ai.chords import encode_timeline_chords
from ai.styles import encode_style

RAW_DATASET = "dataset/raw/maestro"
TOKENS_DIR = "dataset/processed/tokens"

os.makedirs(TOKENS_DIR, exist_ok=True)


# ----------------------------
# TOKENIZER CONFIG
# ----------------------------
config = TokenizerConfig(
    use_programs=True,
    use_tempos=True,
    use_time_signatures=True
)

tokenizer = REMI(config)


# ----------------------------
# FIND MIDI FILES
# ----------------------------
def get_midi_files(root):
    midi_files = []

    for path, _, files in os.walk(root):
        for f in files:
            if f.endswith(".mid") or f.endswith(".midi"):
                midi_files.append(os.path.join(path, f))

    return midi_files


# ----------------------------
# ENCODE MIDI
# ----------------------------
def encode_midi(midi_path, style="JAZZ"):

    try:
        midi = MidiFile(midi_path)

        midi_tokens = tokenizer(midi).ids

        # ----------------------------
        # STYLE TOKENS
        # ----------------------------
        style_tokens = encode_style(style)

        # ----------------------------
        # TIMELINE CHORDS
        # ----------------------------
        timeline = extract_chord_timeline(midi_path)

        chord_tokens = encode_timeline_chords(timeline)

        final_tokens = (
            style_tokens
            + chord_tokens
            + midi_tokens
        )

        return final_tokens

    except Exception as e:
        print(f"❌ Failed: {midi_path}")
        print(e)

        return None

# ----------------------------
# SAVE TOKENS
# ----------------------------
def save_tokens(tokens, out_path):
    with open(out_path, "w") as f:
        json.dump(tokens, f)


# ----------------------------
# MAIN
# ----------------------------
def main():
    midi_files = get_midi_files(RAW_DATASET)

    print(f"🎹 Found {len(midi_files)} MIDI files")

    for i, midi_path in enumerate(midi_files):

        tokens = encode_midi(midi_path)

        if tokens is None:
            continue

        out_name = Path(midi_path).stem + ".json"
        out_path = os.path.join(TOKENS_DIR, out_name)

        save_tokens(tokens, out_path)

        if i % 10 == 0:
            print(f"✔ Processed {i}/{len(midi_files)}")


if __name__ == "__main__":
    main()