import torch
from .base_model import BaseMusicModel

class MoonbeamAdapter(BaseMusicModel):
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def generate(self, tokens, max_len=512):
        input_ids = torch.tensor(tokens).unsqueeze(0)

        out = self.model.generate(
            input_ids,
            max_new_tokens=max_len,
            do_sample=True,
            top_p=0.95,
            temperature=0.9
        )

        return out[0].tolist()

    def continue_song(self, tokens):
        return self.generate(tokens)

    def infill(self, tokens, mask):
        # placeholder: future constrained decoding
        return self.generate(tokens)