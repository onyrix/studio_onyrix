import os
import json
import torch

from torch.utils.data import Dataset


TOKENS_DIR = "dataset/processed/tokens"


class MidiTokenDataset(Dataset):

    def __init__(self, seq_len=512, tokens_dir=TOKENS_DIR):
        self.seq_len = seq_len
        self.tokens_dir = tokens_dir

        self.samples = []

        files = os.listdir(self.tokens_dir)

        for f in files:
            path = os.path.join(self.tokens_dir, f)

            with open(path, "r") as fp:
                tokens = json.load(fp)

            for i in range(0, len(tokens) - seq_len - 1, seq_len):

                x = tokens[i:i+seq_len]
                y = tokens[i+1:i+seq_len+1]

                self.samples.append((x, y))

        print(f"Dataset samples: {len(self.samples)}")


    def __len__(self):
        return len(self.samples)


    def __getitem__(self, idx):
        x, y = self.samples[idx]

        return (
            torch.tensor(x, dtype=torch.long),
            torch.tensor(y, dtype=torch.long)
        )
