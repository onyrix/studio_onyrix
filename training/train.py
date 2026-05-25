import argparse
import json

import torch
from torch.utils.data import DataLoader
from transformers import GPT2Config, GPT2LMHeadModel

from ai.config import (
    DEFAULT_MODEL_PATH,
    MODEL_N_EMBD,
    MODEL_N_HEAD,
    MODEL_N_LAYER,
    MODEL_VOCAB_SIZE,
)
from training.dataset import MidiTokenDataset, TOKENS_DIR


def build_model():
    config = GPT2Config(
        vocab_size=MODEL_VOCAB_SIZE,
        n_embd=MODEL_N_EMBD,
        n_layer=MODEL_N_LAYER,
        n_head=MODEL_N_HEAD,
    )
    return GPT2LMHeadModel(config)


def save_model_config(path, seq_len):
    config_path = f"{path}.config.json"
    data = {
        "vocab_size": MODEL_VOCAB_SIZE,
        "n_embd": MODEL_N_EMBD,
        "n_layer": MODEL_N_LAYER,
        "n_head": MODEL_N_HEAD,
        "seq_len": seq_len,
    }

    with open(config_path, "w") as fp:
        json.dump(data, fp, indent=2)

    return config_path


def train(
    tokens_dir=TOKENS_DIR,
    output_path=DEFAULT_MODEL_PATH,
    seq_len=512,
    batch_size=4,
    epochs=10,
    lr=3e-4,
    device=None,
):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    dataset = MidiTokenDataset(seq_len=seq_len, tokens_dir=tokens_dir)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = build_model().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

    for epoch in range(epochs):
        model.train()
        total_loss = 0

        for x, y in loader:
            x = x.to(device)
            y = y.to(device)

            out = model(input_ids=x, labels=y)
            loss = out.loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch} | Loss: {total_loss:.4f}")

    torch.save(model.state_dict(), output_path)
    config_path = save_model_config(output_path, seq_len)

    print(f"Model saved: {output_path}")
    print(f"Config saved: {config_path}")

    return output_path


def parse_args():
    parser = argparse.ArgumentParser(description="Train the Onyrix MIDI language model.")
    parser.add_argument("--tokens-dir", default=TOKENS_DIR)
    parser.add_argument("--output", default=DEFAULT_MODEL_PATH)
    parser.add_argument("--seq-len", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--lr", type=float, default=3e-4)
    return parser.parse_args()


def main():
    args = parse_args()
    train(
        tokens_dir=args.tokens_dir,
        output_path=args.output,
        seq_len=args.seq_len,
        batch_size=args.batch_size,
        epochs=args.epochs,
        lr=args.lr,
    )


if __name__ == "__main__":
    main()
