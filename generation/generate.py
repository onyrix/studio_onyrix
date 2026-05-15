import torch
from transformers import GPT2Config, GPT2LMHeadModel

from miditok import REMI, TokenizerConfig
from miditoolkit import MidiFile

from ai.styles import encode_style

MODEL_PATH = "moonbeam_style_model.pt"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ----------------------------
# TOKENIZER
# ----------------------------
config = TokenizerConfig(
    use_programs=True,
    use_tempos=True,
    use_time_signatures=True
)

tokenizer = REMI(config)


# ----------------------------
# MODEL
# ----------------------------
model_config = GPT2Config(
    vocab_size=12000,
    n_embd=256,
    n_layer=6,
    n_head=8
)

model = GPT2LMHeadModel(model_config)

model.load_state_dict(
    torch.load(MODEL_PATH, map_location=DEVICE)
)

model.to(DEVICE)
model.eval()


# ----------------------------
# LOAD SEED MIDI
# ----------------------------
def load_seed_tokens(midi_path):
    midi = MidiFile(midi_path)

    tokens = tokenizer(midi)

    return tokens.ids[:128]


# ----------------------------
# GENERATE
# ----------------------------
def generate(seed_tokens, max_new_tokens=512):

    input_ids = torch.tensor(seed_tokens).unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        out = model.generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_p=0.95,
            temperature=0.9
        )

    return out[0].cpu().tolist()


# ----------------------------
# SAVE MIDI
# ----------------------------
def save_midi(tokens, out_path):

    midi = tokenizer.decode([tokens])[0]

    midi.dump(out_path)


# ----------------------------
# MAIN
# ----------------------------
from ai.chords import encode_chords


def main():

    seed = load_seed_tokens("input.mid")

    print("🎹 Seed loaded")

    # ----------------------------
    # CHORD CONDITIONING
    # ----------------------------
    chords = [
        "Cmaj7",
        "Am",
        "F",
        "G"
    ]

    chord_tokens = encode_chords(chords)

    conditioned_input = chord_tokens + seed

    print("🎼 Chord conditioning applied")

    style_tokens = encode_style("LOFI")

    conditioned_input = style_tokens + conditioned_input

    generated = generate(conditioned_input)

    print("🧠 Generation complete")

    save_midi(generated, "output/generated_chord.mid")

    print("✔ Saved output/generated_chord.mid")