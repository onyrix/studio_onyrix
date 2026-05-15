STYLE_TOKENS = {
    "CLASSICAL": 7000,
    "JAZZ": 7001,
    "LOFI": 7002,
    "TECHNO": 7003,
    "CINEMATIC": 7004,
    "AMBIENT": 7005,
    "EDM": 7006
}


def encode_style(style):

    style = style.upper()

    if style in STYLE_TOKENS:
        return [STYLE_TOKENS[style]]

    return []