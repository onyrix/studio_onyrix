"""
Advanced Harmony Engine - Corregge problemi di armonia e voice leading

Questo modulo fornisce:
1. Costruzione corretta di accordi con qualità (maggiori, minori, diminuiti)
2. Voice leading a 4 voci stile SATB (Soprano, Alto, Tenore, Basso)
3. Progressioni armoniche funzionali (T-S-D-T)
4. Controlli di registro appropriati
"""

import pretty_midi
import random
from utils import get_scale_notes, NOTE_MAP

# ============================================================================
# QUALITÀ DEGLI ACCORDI PER GRADO DELLA SCALA
# ============================================================================

# Per scala maggiore: I, ii, iii, IV, V, vi, vii°
MAJOR_CHORD_QUALITIES = {
    0: {"type": "major", "intervals": [0, 4, 7]},      # I
    1: {"type": "minor", "intervals": [0, 3, 7]},      # ii
    2: {"type": "minor", "intervals": [0, 3, 7]},      # iii
    3: {"type": "major", "intervals": [0, 4, 7]},      # IV
    4: {"type": "major", "intervals": [0, 4, 7]},      # V
    5: {"type": "minor", "intervals": [0, 3, 7]},      # vi
    6: {"type": "diminished", "intervals": [0, 3, 6]}, # vii°
}

# Per scala minore naturale: i, ii°, III, iv, v, VI, VII
NATURAL_MINOR_CHORD_QUALITIES = {
    0: {"type": "minor", "intervals": [0, 3, 7]},      # i
    1: {"type": "diminished", "intervals": [0, 3, 6]}, # ii°
    2: {"type": "major", "intervals": [0, 4, 7]},      # III
    3: {"type": "minor", "intervals": [0, 3, 7]},      # iv
    4: {"type": "minor", "intervals": [0, 3, 7]},      # v
    5: {"type": "major", "intervals": [0, 4, 7]},      # VI
    6: {"type": "major", "intervals": [0, 4, 7]},      # VII
}

# Per scala minore armonica: i, ii°, III+, iv, V, VI, vii°
HARMONIC_MINOR_CHORD_QUALITIES = {
    0: {"type": "minor", "intervals": [0, 3, 7]},      # i
    1: {"type": "diminished", "intervals": [0, 3, 6]}, # ii°
    2: {"type": "augmented", "intervals": [0, 4, 8]},  # III+
    3: {"type": "minor", "intervals": [0, 3, 7]},      # iv
    4: {"type": "major", "intervals": [0, 4, 7]},      # V
    5: {"type": "major", "intervals": [0, 4, 7]},      # VI
    6: {"type": "diminished", "intervals": [0, 3, 6]}, # vii°
}

# Mappatura tipi di scala -> qualità accordi
SCALE_CHORD_MAP = {
    "major": MAJOR_CHORD_QUALITIES,
    "ionian": MAJOR_CHORD_QUALITIES,
    "natural_minor": NATURAL_MINOR_CHORD_QUALITIES,
    "aeolian": NATURAL_MINOR_CHORD_QUALITIES,
    "harmonic_minor": HARMONIC_MINOR_CHORD_QUALITIES,
    "dorian": NATURAL_MINOR_CHORD_QUALITIES,  # Approssimato
    "phrygian": NATURAL_MINOR_CHORD_QUALITIES,
    "mixolydian": MAJOR_CHORD_QUALITIES,
    "lydian": MAJOR_CHORD_QUALITIES,
    "locrian": {  # Tutti diminuiti o semi-diminuiti
        i: {"type": "diminished", "intervals": [0, 3, 6]} for i in range(7)
    },
}


# ============================================================================
# FUNZIONI DI VOICE LEADING CORRETTO
# ============================================================================

def build_chord_with_quality(root_note, quality_info, octave=4):
    """
    Costruisce un accordo con la qualità corretta partendo dalla nota radice.
    
    Args:
        root_note: Nota radice (0-11, dove 0=C, 1=C#, ecc.)
        quality_info: Dict con "type" e "intervals"
        octave: Ottava di partenza (default: 4)
    
    Returns:
        list: Note dell'accordo come MIDI note numbers
    """
    intervals = quality_info["intervals"]
    root_midi = root_note + (octave * 12)
    
    chord_notes = [root_midi + interval for interval in intervals]
    return chord_notes


def voice_lead_satb(prev_chord, next_chord, voice_ranges):
    """
    Voice leading a 4 voci (SATB) per transizioni fluide.
    
    Args:
        prev_chord: Note dell'accordo precedente [S, A, T, B]
        next_chord: Note dell'accordo successivo (non voice-led)
        voice_ranges: Dict con i range per ogni voce
                     {"soprano": (C4, C6), "alto": (G3, G5), ...}
    
    Returns:
        list: Note dell'accordo successivo con voice leading [S, A, T, B]
    """
    if not prev_chord or len(prev_chord) != 4:
        # Se non c'è accordo precedente, usa posizione fondamentale
        return position_chord_satb(next_chord, voice_ranges)
    
    result = []
    used_notes = []
    
    # Ordina le note dell'accordo precedente per voce (dalla più alta alla più bassa)
    prev_sorted = sorted(prev_chord, reverse=True)
    
    # Per ogni voce (dalla più alta alla più bassa)
    for i, voice_name in enumerate(["soprano", "alto", "tenor", "bass"]):
        voice_range = voice_ranges[voice_name]
        
        # Trova la nota nell'accordo successivo che minimizza il movimento
        best_note = None
        best_distance = float('inf')
        
        for note in next_chord:
            # Porta la nota nell'ottava corretta per questa voce
            note_in_range = move_to_octave_range(note, voice_range)
            
            # Calcola la distanza dalla voce precedente
            if i < len(prev_sorted):
                distance = abs(note_in_range - prev_sorted[i])
            else:
                distance = abs(note_in_range - voice_range[0])
            
            # Penalizza salti grandi
            if distance < best_distance and note_in_range not in used_notes:
                best_distance = distance
                best_note = note_in_range
        
        if best_note is not None:
            result.append(best_note)
            used_notes.append(best_note)
    
    return result if len(result) == 4 else position_chord_satb(next_chord, voice_ranges)


def position_chord_satb(chord_notes, voice_ranges):
    """
    Posiziona un accordo in posizione SATB standard.
    
    Args:
        chord_notes: Note dell'accordo (triade o settima)
        voice_ranges: Range per ogni voce
    
    Returns:
        list: 4 note posizionate per SATB
    """
    # Assicura che ci siano almeno 3 note
    if len(chord_notes) < 3:
        chord_notes = chord_notes + [chord_notes[0] + 12] * (3 - len(chord_notes))
    
    # Basso: nota più bassa
    bass = min(chord_notes)
    bass = move_to_octave_range(bass, voice_ranges["bass"])
    
    # Le altre note nelle voci superiori
    other_notes = sorted([n for n in chord_notes if n != bass], reverse=True)
    
    # Se abbiamo solo 3 note, raddoppia la nota più alta
    if len(other_notes) == 2:
        other_notes.append(other_notes[0] + 12)
    
    soprano = move_to_octave_range(other_notes[0], voice_ranges["soprano"])
    alto = move_to_octave_range(other_notes[1], voice_ranges["alto"])
    tenor = move_to_octave_range(other_notes[2] if len(other_notes) > 2 else other_notes[1] - 12, 
                                  voice_ranges["tenor"])
    
    return [soprano, alto, tenor, bass]


def move_to_octave_range(note, voice_range):
    """
    Sposta una nota nell'ottava corretta per un range vocale.
    
    Args:
        note: Nota MIDI
        voice_range: Tuple (min_note, max_note)
    
    Returns:
        int: Nota nell'ottava corretta
    """
    min_note, max_note = voice_range
    
    # Porta la nota nel range
    while note > max_note:
        note -= 12
    while note < min_note:
        note += 12
    
    return note


# ============================================================================
# RANGE VOCALI STANDARD
# ============================================================================

STANDARD_VOICE_RANGES = {
    "soprano": (60, 84),   # C4 - C6
    "alto": (53, 77),      # G3 - G5
    "tenor": (48, 72),     # C3 - C5
    "bass": (36, 60),      # C2 - C4
}

# Range per strumenti (più ampi)
INSTRUMENT_VOICE_RANGES = {
    "soprano": (60, 96),   # C4 - C8
    "alto": (48, 84),      # C3 - C6
    "tenor": (48, 76),     # C3 - D5
    "bass": (24, 48),      # C1 - C3
}


# ============================================================================
# COSTRUZIONE ACCORDI CON QUALITÀ CORRETTA
# ============================================================================

def get_chord_for_degree(scale_name, degree, complexity=0.3, octave=4):
    """
    Ottiene un accordo per un grado specifico con qualità corretta.
    
    Args:
        scale_name: Nome della scala (es. "C_major", "D_minor")
        degree: Grado della scala (0-6)
        complexity: 0.0-1.0 (0=triade, 1=accordi estesi)
        octave: Ottava di partenza
    
    Returns:
        list: Note dell'accordo
    """
    # Estrai tonica e tipo di scala
    parts = scale_name.split("_")
    tonic = parts[0]
    scale_type = "_".join(parts[1:]) if len(parts) > 1 else "major"
    
    # Ottieni note della scala
    scale = get_scale_notes(scale_name, scale_type)
    
    # Ottieni qualità dell'accordo per questo grado
    chord_qualities = SCALE_CHORD_MAP.get(scale_type, MAJOR_CHORD_QUALITIES)
    quality = chord_qualities.get(degree % 7, {"type": "minor", "intervals": [0, 3, 7]})
    
    # Nota radice per questo grado
    root_note = scale[degree % 7] % 12  # Porta in una singola ottava
    
    # Costruisci accordo base
    chord = build_chord_with_quality(root_note, quality, octave)
    
    # Aggiungi estensioni se complessità alta
    if complexity >= 0.5:
        chord = add_chord_extensions(chord, scale, degree, quality, complexity)
    
    return chord


def add_chord_extensions(chord, scale, degree, quality, complexity):
    """
    Aggiunge estensioni (7th, 9th, 11th, 13th) agli accordi.
    
    Args:
        chord: Accordo base
        scale: Scala di riferimento
        degree: Grado dell'accordo
        quality: Qualità dell'accordo
        complexity: Livello di complessità
    
    Returns:
        list: Accordo con estensioni
    """
    extended = chord.copy()
    
    # Aggiungi 7th
    if complexity >= 0.4:
        seventh_degree = (degree + 6) % 7
        seventh = scale[seventh_degree]
        # Porta nell'ottava corretta
        while seventh < max(chord):
            seventh += 12
        extended.append(seventh)
    
    # Aggiungi 9th
    if complexity >= 0.6:
        ninth_degree = (degree + 8) % 7
        ninth = scale[ninth_degree] + 12  # Una ottava sopra
        while ninth < max(extended):
            ninth += 12
        extended.append(ninth)
    
    # Aggiungi 11th o 13th
    if complexity >= 0.8:
        if random.random() < 0.5:
            eleventh_degree = (degree + 10) % 7
            eleventh = scale[eleventh_degree] + 12
            while eleventh < max(extended):
                eleventh += 12
            extended.append(eleventh)
        else:
            thirteenth_degree = (degree + 12) % 7
            thirteenth = scale[thirteenth_degree] + 12
            while thirteenth < max(extended):
                thirteenth += 12
            extended.append(thirteenth)
    
    return extended


# ============================================================================
# PROGRESSIONI ARMONICHE FUNZIONALI
# ============================================================================

# Funzioni armoniche: T (tonica), S (sottodominante), D (dominante)
HARMONIC_FUNCTIONS = {
    0: "T",   # I - Tonica
    1: "S",   # ii - Sottodominante
    2: "T",   # iii - Tonica (debole)
    3: "S",   # IV - Sottodominante
    4: "D",   # V - Dominante
    5: "T",   # vi - Tonica (debole)
    6: "D",   # vii° - Dominante
}

# Progressioni funzionali tipiche
FUNCTIONAL_PROGRESSIONS = {
    "standard": [0, 4, 5, 3],      # I - V - vi - IV
    "jazz": [0, 1, 4, 3],          # I - ii - V - vi
    "classical": [0, 3, 4, 0],     # I - IV - V - I
    "pop": [0, 4, 3, 5],           # I - V - IV - vi
    "blues": [0, 3, 0, 4],         # I - IV - I - V
    "ii_v_i": [1, 4, 0],           # ii - V - I
    "plagal": [0, 3, 0],           # I - IV - I
    "andalusian": [0, 6, 5, 4],    # i - VII - VI - V (frigia)
}


def get_functional_progression(style, length=4):
    """
    Ottiene una progressione funzionale appropriata per lo stile.
    
    Args:
        style: Nome dello stile
        length: Numero di accordi
    
    Returns:
        list: Gradi della progressione
    """
    # Mappa stili a progressioni tipiche
    style_progressions = {
        "trap": [0, 4, 3],
        "drill": [0, 4, 3],
        "boom_bap": [0, 1, 4, 3],
        "lofi": [0, 3, 5, 3],
        "house": [0, 4, 3],
        "deep_house": [0, 1, 4, 3],
        "techno": [0, 4],
        "dubstep": [0, 4, 3],
        "dnb": [0, 4, 3],
        "ambient": [0, 3, 5],
        "cinematic": [0, 3, 4, 0],
        "rock": [0, 4, 5, 3],
        "funk": [0, 4, 3],
        "jazz": [1, 4, 0],
        "synthpop": [0, 4, 5, 3],
        "synthwave": [0, 3, 4, 0],
        "retrowave": [0, 3, 4, 0],
        "outrun": [0, 3, 4, 0],
        "darkwave": [0, 1, 3],
        "ebm": [0, 4, 3],
        "electro": [0, 4, 3],
        "idm": [0, 2, 6, 5],
        "glitch": [0, 2, 4],
        "electronic_pop": [0, 4, 5, 3],
    }
    
    progression = style_progressions.get(style, FUNCTIONAL_PROGRESSIONS["standard"])
    
    # Estendi se necessario
    while len(progression) < length:
        progression = progression + progression[:length - len(progression)]
    
    return progression[:length]