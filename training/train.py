import torch
from torch.utils.data import DataLoader

from transformers import GPT2Config, GPT2LMHeadModel

from training.dataset import MidiTokenDataset


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ----------------------------
# DATASET
# ----------------------------
dataset = MidiTokenDataset(seq_len=512)

loader = DataLoader(
    dataset,
    batch_size=4,
    shuffle=True
)


# ----------------------------
# MODEL
# ----------------------------
config = GPT2Config(
    vocab_size=5000,
    n_embd=256,
    n_layer=6,
    n_head=8
)

model = GPT2LMHeadModel(config).to(DEVICE)

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=3e-4
)


# ----------------------------
# TRAIN LOOP
# ----------------------------
for epoch in range(10):

    model.train()

    total_loss = 0

    for x, y in loader:

        x = x.to(DEVICE)
        y = y.to(DEVICE)

        out = model(
            input_ids=x,
            labels=y
        )

        loss = out.loss

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch} | Loss: {total_loss:.4f}")


# ----------------------------
# SAVE MODEL
# ----------------------------
torch.save(
    model.state_dict(),
    "moonbeam_style_model.pt"
)

print("✅ Model saved")