from ai.config import STYLE_TOKEN_START


STYLE_TOKENS = {
    "CLASSICAL": STYLE_TOKEN_START,
    "JAZZ": STYLE_TOKEN_START + 1,
    "LOFI": STYLE_TOKEN_START + 2,
    "TECHNO": STYLE_TOKEN_START + 3,
    "CINEMATIC": STYLE_TOKEN_START + 4,
    "AMBIENT": STYLE_TOKEN_START + 5,
    "EDM": STYLE_TOKEN_START + 6
}


def encode_style(style):

    style = style.upper()

    if style in STYLE_TOKENS:
        return [STYLE_TOKENS[style]]

    return []
