import random

NOTE_MAP = {
    "C":60,"C#":61,"D":62,"D#":63,"E":64,
    "F":65,"F#":66,"G":67,"G#":68,"A":69,"A#":70,"B":71
}

def get_scale_notes(key, scale_type="major"):
    root,_ = key.split("_")
    root_midi = NOTE_MAP[root]

    scales = {

        # SCALE MAGGIORI / MINORI
        "major":            [0, 2, 4, 5, 7, 9, 11],
        "natural_minor":    [0, 2, 3, 5, 7, 8, 10],
        "harmonic_minor":   [0, 2, 3, 5, 7, 8, 11],
        "melodic_minor":    [0, 2, 3, 5, 7, 9, 11],

        # MODI DELLA MAGGIORE
        "ionian":           [0, 2, 4, 5, 7, 9, 11],
        "dorian":           [0, 2, 3, 5, 7, 9, 10],
        "phrygian":         [0, 1, 3, 5, 7, 8, 10],
        "lydian":           [0, 2, 4, 6, 7, 9, 11],
        "mixolydian":       [0, 2, 4, 5, 7, 9, 10],
        "aeolian":          [0, 2, 3, 5, 7, 8, 10],
        "locrian":          [0, 1, 3, 5, 6, 8, 10],

        # MODI DELLA MELODIC MINOR
        "melodic_minor_2":  [0, 1, 3, 5, 7, 9, 10],   # Dorian b2
        "lydian_aug":       [0, 2, 4, 6, 8, 9, 11],
        "lydian_dom":       [0, 2, 4, 6, 7, 9, 10],
        "mixolydian_b6":    [0, 2, 4, 5, 7, 8, 10],
        "locrian_nat2":     [0, 2, 3, 5, 6, 8, 10],
        "super_locrian":    [0, 1, 3, 4, 6, 8, 10],

        # SCALE SIMMETRICHE
        "whole_tone":       [0, 2, 4, 6, 8, 10],
        "diminished_half":  [0, 1, 3, 4, 6, 7, 9, 10],
        "diminished_whole": [0, 2, 3, 5, 6, 8, 9, 11],

        # BLUES / PENTATONICHE
        "major_pentatonic": [0, 2, 4, 7, 9],
        "minor_pentatonic": [0, 3, 5, 7, 10],
        "blues":            [0, 3, 5, 6, 7, 10],

        # SCALE ETNICHE / SPECIALI
        "chromatic":        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        "phrygian_dominant":[0, 1, 4, 5, 7, 8, 10],
        "hungarian_minor":  [0, 2, 3, 6, 7, 8, 11],
        "neapolitan_minor": [0, 1, 3, 5, 7, 8, 11],
        "neapolitan_major": [0, 1, 3, 5, 7, 9, 11],
    }

    return [root_midi+i for i in scales.get(scale_type, scales["natural_minor"])]

def build_chords(scale):
    return [[scale[i], scale[(i+2)%7], scale[(i+4)%7]] for i in range(len(scale))]

def select_progression(chords, chaos):
    patterns = [

        # POP / ROCK
        [0, 4, 5, 3],        # I–V–vi–IV
        [0, 3, 4],           # I–vi–V
        [0, 5, 3, 4],        # I–IV–vi–V
        [0, 4, 3, 5],        # I–V–vi–IV (var)
        [0, 3, 5, 4],        # I–vi–IV–V

        # CLASSICHE
        [0, 3, 4, 0],        # I–vi–V–I
        [0, 5, 0, 4],        # I–IV–I–V
        [0, 1, 4, 0],        # I–ii–V–I
        [0, 6, 3, 4],        # I–vii°–vi–V

        # SOUNDTRACK / AMBIENT
        [0, 5, 3, 6],        # I–IV–vi–vii°
        [0, 2, 5, 3],        # I–iii–IV–vi
        [0, 3, 5],           # I–vi–IV
        [0, 6],              # I–vii°
        [0, 2, 4, 6],        # I–iii–V–vii°

        # BLUES / ROCK
        [0, 3, 4],           # I–IV–V
        [0, 0, 3, 4],        # I–I–IV–V
        [0, 3, 0, 4],        # I–IV–I–V

        # JAZZ / NEO-SOUL
        [0, 1, 4, 3],        # I–ii–V–vi
        [2, 5, 1, 4],        # iii–vi–ii–V
        [5, 1, 4, 0],        # vi–ii–V–I
        [1, 4, 0],           # ii–V–I
        [3, 6, 2, 5],        # IV–vii°–iii–vi

        # MODALI / SPERIMENTALI
        [0, 2, 6, 5],        # I–iii–vii°–IV
        [0, 5, 2, 3],        # I–IV–iii–vi
        [6, 3, 0],           # vii°–vi–I
        [5, 4, 3, 2],        # IV–V–vi–iii

        # MINIMAL / LOOP
        [0, 3],
        [0, 4],
        [3, 4],
        [5, 0],
    ]

    pattern = random.choice(patterns)

    if random.random() < chaos:
        pattern = [random.randint(0, 6) for _ in pattern]

    return [chords[i % 7] for i in pattern]