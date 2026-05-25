import os

import torch
from transformers import GPT2LMHeadModel, GPT2Config

from ai.config import (
    DEFAULT_MODEL_PATH,
    MODEL_N_EMBD,
    MODEL_N_HEAD,
    MODEL_N_LAYER,
    MODEL_VOCAB_SIZE,
)


class MidiTransformerModel:
    def __init__(self, vocab_size=MODEL_VOCAB_SIZE, checkpoint_path=DEFAULT_MODEL_PATH, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        config = GPT2Config(
            vocab_size=vocab_size,
            n_embd=MODEL_N_EMBD,
            n_layer=MODEL_N_LAYER,
            n_head=MODEL_N_HEAD
        )

        self.model = GPT2LMHeadModel(config).to(self.device)
        self.checkpoint_loaded = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
            self.checkpoint_loaded = True

        self.model.eval()

    def generate(self, input_ids, max_len=512):
        input_ids = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0).to(self.device)
        attention_mask = torch.ones_like(input_ids)

        with torch.no_grad():
            out = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=max_len,
                do_sample=True,
                temperature=0.9,
                top_p=0.95,
                pad_token_id=0
            )

        return out[0].cpu().tolist()
