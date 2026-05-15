CHORD_VOCAB = {}

START_TOKEN = 5000


def build_chord_vocab():

    roots = [
        "C", "C#", "D", "Eb", "E",
        "F", "F#", "G", "Ab", "A",
        "Bb", "B"
    ]

    qualities = [
        "",
        "m",
        "7",
        "maj7",
        "m7",
        "dim"
    ]

    idx = START_TOKEN

    for root in roots:
        for q in qualities:

            name = root + q

            CHORD_VOCAB[name] = idx

            idx += 1


build_chord_vocab()


def encode_chords(chords):

    tokens = []

    for chord in chords:

        if chord in CHORD_VOCAB:
            tokens.append(CHORD_VOCAB[chord])

    return tokens

TIME_OFFSET_BASE = 6000


def encode_timeline_chords(timeline):

    tokens = []

    for item in timeline:

        chord_name = item["chord"]

        if chord_name not in CHORD_VOCAB:
            continue

        chord_token = CHORD_VOCAB[chord_name]

        # quantizzazione tempo
        time_bucket = int(item["time"] * 4)

        time_token = TIME_OFFSET_BASE + time_bucket

        tokens.append(time_token)
        tokens.append(chord_token)

    return tokens