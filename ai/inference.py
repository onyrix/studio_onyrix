class InferenceEngine:
    def __init__(self, model):
        self.model = model

    def generate_continuation(self, tokens):
        return self.model.continue_song(tokens)

    def generate_infill(self, tokens, mask=None):
        return self.model.infill(tokens, mask)