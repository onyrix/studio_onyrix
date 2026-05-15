import torch
from transformers import GPT2LMHeadModel, GPT2Config

class MidiTransformerModel:
    def __init__(self, vocab_size=5000):
        config = GPT2Config(
            vocab_size=vocab_size,
            n_embd=256,
            n_layer=6,
            n_head=8
        )

        self.model = GPT2LMHeadModel(config)

    def generate(self, input_ids, max_len=512):
        input_ids = torch.tensor(input_ids).unsqueeze(0)

        out = self.model.generate(
            input_ids,
            max_new_tokens=max_len,
            do_sample=True,
            temperature=0.9,
            top_p=0.95
        )

        return out[0].tolist()