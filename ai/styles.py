from ai.config import STYLE_TOKEN_START
from generation.music_config import STYLE_LIBRARY


STYLE_TOKENS = {
    style.upper(): STYLE_TOKEN_START + index
    for index, style in enumerate(sorted(STYLE_LIBRARY))
}


def encode_style(style):
    style = style.upper()

    if style in STYLE_TOKENS:
        return [STYLE_TOKENS[style]]

    return []
