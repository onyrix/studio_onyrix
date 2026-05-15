class BaseMusicModel:
    def generate(self, tokens, max_len=512):
        raise NotImplementedError

    def continue_song(self, tokens):
        raise NotImplementedError

    def infill(self, tokens, mask):
        raise NotImplementedError