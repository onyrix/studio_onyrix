import torch
import random

from transformers import GPT2Config, GPT2LMHeadModel

from miditok import REMI, TokenizerConfig
from miditoolkit import MidiFile

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
# LOAD MIDI TOKENS
# ----------------------------
def load_tokens(path):

    midi = MidiFile(path)

    tokens = tokenizer(midi)

    return tokens.ids


# ----------------------------
# MASK REGION
# ----------------------------
def mask_region(tokens, start=128, length=128):

    masked = tokens[:]

    for i in range(start, min(start + length, len(masked))):
        masked[i] = random.randint(0, 10)

    return masked


# ----------------------------
# INFILL GENERATION
# ----------------------------
def infill(tokens, start=128, length=128):

    input_ids = torch.tensor(tokens[:start]).unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        out = model.generate(
            input_ids=input_ids,
            max_new_tokens=length,
            do_sample=True,
            top_p=0.95,
            temperature=0.9
        )

    generated = out[0].cpu().tolist()

    final = (
        tokens[:start]
        + generated[start:]
        + tokens[start + length:]
    )

    return final


# ----------------------------
# SAVE MIDI
# ----------------------------
def save(tokens, out_path):

    midi = tokenizer.decode([tokens])[0]

    midi.dump(out_path)


# ----------------------------
# MAIN
# ----------------------------
def main():

    tokens = load_tokens("input.mid")

    print("🎹 MIDI loaded")

    out = infill(tokens)

    print("🧠 Infill complete")

    save(out, "output/infilled.mid")

    print("✔ Saved output/infilled.mid")


if __name__ == "__main__":
    main()