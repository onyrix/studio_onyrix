"""
Instrument Mapping Module - Gestione corretta degli strumenti MIDI

Questo modulo fornisce:
1. Nomi strumenti GM (General MIDI) validati e corretti
2. Mappatura da nomi "umanizzati" a nomi GM ufficiali
3. Sistema di fallback con logging
4. Alternative strumentali per ogni ruolo
"""

import pretty_midi
import random

# ============================================================================
# NOMI STRUMENTI GM UFFICIALI (General MIDI Level 1)
# ============================================================================
# Questi sono i nomi esatti che pretty_midi si aspetta per instrument_name_to_program()

GM_INSTRUMENT_NAMES = {
    # Piano
    "Acoustic Grand Piano": 0,
    "Bright Acoustic Piano": 1,
    "Electric Grand Piano": 2,
    "Honky-tonk Piano": 3,
    "Electric Piano 1": 4,
    "Electric Piano 2": 5,
    "Harpsichord": 6,
    "Clavi": 7,
    
    # Chromatic Percussion
    "Celesta": 8,
    "Glockenspiel": 9,
    "Music Box": 10,
    "Vibraphone": 11,
    "Marimba": 12,
    "Xylophone": 13,
    "Tubular Bells": 14,
    "Dulcimer": 15,
    
    # Organ
    "Drawbar Organ": 16,
    "Percussive Organ": 17,
    "Rock Organ": 18,
    "Church Organ": 19,
    "Reed Organ": 20,
    "Accordion": 21,
    "Harmonica": 22,
    "Tango Accordion": 23,
    
    # Guitar
    "Acoustic Guitar (nylon)": 24,
    "Acoustic Guitar (steel)": 25,
    "Electric Guitar (jazz)": 26,
    "Electric Guitar (clean)": 27,
    "Electric Guitar (muted)": 28,
    "Overdriven Guitar": 29,
    "Distortion Guitar": 30,
    "Guitar Harmonics": 31,
    
    # Bass
    "Acoustic Bass": 32,
    "Electric Bass (finger)": 33,
    "Electric Bass (pick)": 34,
    "Fretless Bass": 35,
    "Slap Bass 1": 36,
    "Slap Bass 2": 37,
    "Synth Bass 1": 38,
    "Synth Bass 2": 39,
    
    # Strings
    "Violin": 40,
    "Viola": 41,
    "Cello": 42,
    "Contrabass": 43,
    "Tremolo Strings": 44,
    "Pizzicato Strings": 45,
    "Orchestral Harp": 46,
    "Timpani": 47,
    
    # Ensemble
    "String Ensemble 1": 48,
    "String Ensemble 2": 49,
    "Synth Strings 1": 50,
    "Synth Strings 2": 51,
    "Choir Aahs": 52,
    "Voice Oohs": 53,
    "Synth Voice": 54,
    "Orchestra Hit": 55,
    
    # Brass
    "Trumpet": 56,
    "Trombone": 57,
    "Tuba": 58,
    "Muted Trumpet": 59,
    "French Horn": 60,
    "Brass Section": 61,
    "Synth Brass 1": 62,
    "Synth Brass 2": 63,
    
    # Reed
    "Soprano Sax": 64,
    "Alto Sax": 65,
    "Tenor Sax": 66,
    "Baritone Sax": 67,
    "Oboe": 68,
    "English Horn": 69,
    "Bassoon": 70,
    "Clarinet": 71,
    
    # Pipe
    "Piccolo": 72,
    "Flute": 73,
    "Recorder": 74,
    "Pan Flute": 75,
    "Blown Bottle": 76,
    "Shakuhachi": 77,
    "Whistle": 78,
    "Ocarina": 79,
    
    # Synth Lead
    "Lead 1 (square)": 80,
    "Lead 2 (sawtooth)": 81,
    "Lead 3 (calliope)": 82,
    "Lead 4 (chiff)": 83,
    "Lead 5 (charang)": 84,
    "Lead 6 (voice)": 85,
    "Lead 7 (fifths)": 86,
    "Lead 8 (bass + lead)": 87,
    
    # Synth Pad
    "Pad 1 (new age)": 88,
    "Pad 2 (warm)": 89,
    "Pad 3 (polysynth)": 90,
    "Pad 4 (choir)": 91,
    "Pad 5 (bowed)": 92,
    "Pad 6 (metallic)": 93,
    "Pad 7 (halo)": 94,
    "Pad 8 (sweep)": 95,
    
    # Synth Effects
    "FX 1 (rain)": 96,
    "FX 2 (soundtrack)": 97,
    "FX 3 (crystal)": 98,
    "FX 4 (atmosphere)": 99,
    "FX 5 (brightness)": 100,
    "FX 6 (goblins)": 101,
    "FX 7 (echoes)": 102,
    "FX 8 (sci-fi)": 103,
    
    # Ethnic
    "Sitar": 104,
    "Banjo": 105,
    "Shamisen": 106,
    "Koto": 107,
    "Kalimba": 108,
    "Bag pipe": 109,
    "Fiddle": 110,
    "Shanai": 111,
    
    # Percussive
    "Tinkle Bell": 112,
    "Agogo": 113,
    "Steel Drums": 114,
    "Woodblock": 115,
    "Taiko Drum": 116,
    "Melodic Tom": 117,
    "Synth Drum": 118,
    "Reverse Cymbal": 119,
    
    # Sound Effects
    "Guitar Fret Noise": 120,
    "Breath Noise": 121,
    "Seashore": 122,
    "Bird Tweet": 123,
    "Telephone Ring": 124,
    "Helicopter": 125,
    "Applause": 126,
    "Gunshot": 127,
}

# ============================================================================
# MAPPATURA NOMI "UMANIZZATI" -> NOMI GM UFFICIALI
# ============================================================================
# Permette di usare nomi più semplici che vengono convertiti automaticamente

HUMAN_TO_GM_MAPPING = {
    # Nomi errati/umanizzati -> Nomi GM corretti
    "Square Lead": "Lead 1 (square)",
    "Sawtooth Lead": "Lead 2 (sawtooth)",
    "Calliope Lead": "Lead 3 (calliope)",
    "Chiff Lead": "Lead 4 (chiff)",
    "Charang Lead": "Lead 5 (charang)",
    "Voice Lead": "Lead 6 (voice)",
    "Fifths Lead": "Lead 7 (fifths)",
    "Bass Lead": "Lead 8 (bass + lead)",
    
    "New Age Pad": "Pad 1 (new age)",
    "Warm Pad": "Pad 2 (warm)",
    "Polysynth Pad": "Pad 3 (polysynth)",
    "Choir Pad": "Pad 4 (choir)",
    "Bowed Pad": "Pad 5 (bowed)",
    "Metallic Pad": "Pad 6 (metallic)",
    "Halo Pad": "Pad 7 (halo)",
    "Sweep Pad": "Pad 8 (sweep)",
    
    "Synth Bass 1": "Synth Bass 1",
    "Synth Bass 2": "Synth Bass 2",
    "Electric Bass": "Electric Bass (finger)",
    "Finger Bass": "Electric Bass (finger)",
    "Pick Bass": "Electric Bass (pick)",
    "Fretless Bass": "Fretless Bass",
    "Slap Bass": "Slap Bass 1",
    "Acoustic Bass": "Acoustic Bass",
    
    "Grand Piano": "Acoustic Grand Piano",
    "Bright Piano": "Bright Acoustic Piano",
    "Electric Piano": "Electric Piano 1",
    "EPiano": "Electric Piano 1",
    "Rhodes": "Electric Piano 1",
    "DX Piano": "Electric Piano 2",
    
    "Clean Guitar": "Electric Guitar (clean)",
    "Jazz Guitar": "Electric Guitar (jazz)",
    "Muted Guitar": "Electric Guitar (muted)",
    "Overdrive Guitar": "Overdriven Guitar",
    "Distortion Guitar": "Distortion Guitar",
    "Nylon Guitar": "Acoustic Guitar (nylon)",
    "Steel Guitar": "Acoustic Guitar (steel)",
    
    "String Ensemble": "String Ensemble 1",
    "Synth Strings": "Synth Strings 1",
    "Choir": "Choir Aahs",
    "Voice": "Synth Voice",
    "Orchestra Hit": "Orchestra Hit",
    "Orchestra Strings": "String Ensemble 1",  # Correzione nome errato
    
    "Synth Brass": "Synth Brass 1",
    "Brass Section": "Brass Section",
    "French Horn": "French Horn",
    "Trumpet": "Trumpet",
    "Trombone": "Trombone",
    
    "Soprano Sax": "Soprano Sax",
    "Alto Sax": "Alto Sax",
    "Tenor Sax": "Tenor Sax",
    "Baritone Sax": "Baritone Sax",
    
    "Square": "Lead 1 (square)",
    "Sawtooth": "Lead 2 (sawtooth)",
    "Saw": "Lead 2 (sawtooth)",
}

# ============================================================================
# ALTERNATIVE STRUMENTALI PER RUOLO
# ============================================================================
# Liste di strumenti appropriati per ogni ruolo, organizzati per "vibe"

INSTRUMENT_ALTERNATIVES = {
    "lead": {
        "synth": [
            "Lead 1 (square)",
            "Lead 2 (sawtooth)",
            "Lead 3 (calliope)",
            "Lead 4 (chiff)",
            "Lead 5 (charang)",
            "Lead 6 (voice)",
            "Lead 7 (fifths)",
        ],
        "brass": [
            "Synth Brass 1",
            "Synth Brass 2",
            "Brass Section",
            "Trumpet",
        ],
        "guitar": [
            "Electric Guitar (clean)",
            "Electric Guitar (jazz)",
            "Overdriven Guitar",
            "Distortion Guitar",
        ],
        "keys": [
            "Electric Piano 1",
            "Electric Piano 2",
            "Acoustic Grand Piano",
            "Honky-tonk Piano",
        ],
        "sax": [
            "Soprano Sax",
            "Alto Sax",
            "Tenor Sax",
        ],
        "strings": [
            "Violin",
            "Synth Strings 1",
            "String Ensemble 1",
        ],
        "voice": [
            "Lead 6 (voice)",
            "Choir Aahs",
            "Voice Oohs",
            "Synth Voice",
        ],
        "ethnic": [
            "Sitar",
            "Shakuhachi",
            "Pan Flute",
            "Kalimba",
        ],
    },
    "pad": {
        "soft": [
            "Pad 1 (new age)",
            "Pad 2 (warm)",
            "Pad 5 (bowed)",
        ],
        "choir": [
            "Pad 4 (choir)",
            "Choir Aahs",
            "Voice Oohs",
        ],
        "synth": [
            "Pad 3 (polysynth)",
            "Synth Strings 1",
            "Synth Strings 2",
        ],
        "atmospheric": [
            "Pad 6 (metallic)",
            "Pad 7 (halo)",
            "Pad 8 (sweep)",
            "FX 4 (atmosphere)",
        ],
        "dark": [
            "Pad 5 (bowed)",
            "Pad 6 (metallic)",
            "FX 2 (soundtrack)",
        ],
    },
    "bass": {
        "synth": [
            "Synth Bass 1",
            "Synth Bass 2",
        ],
        "electric": [
            "Electric Bass (finger)",
            "Electric Bass (pick)",
            "Fretless Bass",
        ],
        "slap": [
            "Slap Bass 1",
            "Slap Bass 2",
        ],
        "acoustic": [
            "Acoustic Bass",
            "Contrabass",
        ],
        "deep": [
            "Synth Bass 2",
            "Synth Bass 1",
            "Fretless Bass",
        ],
    },
}

# ============================================================================
# FUNZIONI HELPER
# ============================================================================

def normalize_instrument_name(name):
    """
    Converte un nome strumento "umanizzato" nel nome GM ufficiale.
    
    Args:
        name: Nome strumento (può essere già GM o "umanizzato")
    
    Returns:
        str: Nome GM ufficiale
    """
    if not name:
        return "Lead 1 (square)"
    
    # Se è già un nome GM valido, restituiscilo
    if name in GM_INSTRUMENT_NAMES:
        return name
    
    # Prova a convertire da nome umanizzato
    if name in HUMAN_TO_GM_MAPPING:
        return HUMAN_TO_GM_MAPPING[name]
    
    # Prova una corrispondenza approssimativa (case-insensitive)
    name_lower = name.lower().strip()
    for gm_name in GM_INSTRUMENT_NAMES:
        if gm_name.lower() == name_lower:
            return gm_name
    
    # Se non troviamo corrispondenza, logghiamo e usiamo un default
    print(f"Warning: Instrument '{name}' not found in GM standard. Using 'Lead 1 (square)' as fallback.")
    return "Lead 1 (square)"


def get_instrument_program(name):
    """
    Ottiene il programma MIDI per un nome strumento.
    
    Args:
        name: Nome strumento (GM o umanizzato)
    
    Returns:
        int: Numero programma MIDI (0-127)
    """
    gm_name = normalize_instrument_name(name)
    try:
        program = pretty_midi.instrument_name_to_program(gm_name)
        return program
    except Exception as e:
        print(f"Error converting instrument '{name}' to program: {e}")
        # Fallback basato sul tipo di strumento
        if "bass" in name.lower():
            return 33  # Electric Bass (finger)
        elif "lead" in name.lower():
            return 80  # Lead 1 (square)
        elif "pad" in name.lower():
            return 88  # Pad 1 (new age)
        else:
            return 0  # Acoustic Grand Piano


def select_random_instrument(role, category=None):
    """
    Seleziona casualmente uno strumento da una categoria.
    
    Args:
        role: Ruolo strumento ("lead", "pad", "bass")
        category: Sottocategoria opzionale (es. "synth", "soft", ecc.)
    
    Returns:
        str: Nome strumento GM
    """
    if role not in INSTRUMENT_ALTERNATIVES:
        return "Lead 1 (square)"
    
    alternatives = INSTRUMENT_ALTERNATIVES[role]
    
    if category and category in alternatives:
        return random.choice(alternatives[category])
    
    # Seleziona da tutte le alternative
    all_instruments = []
    for instruments in alternatives.values():
        all_instruments.extend(instruments)
    
    return random.choice(all_instruments)


def get_style_instruments_with_alternatives(style_instruments):
    """
    Espande la configurazione strumenti di uno stile con le alternative.
    
    Args:
        style_instruments: Dict con strumenti dello stile (può avere stringhe o liste)
    
    Returns:
        dict: Configurazione espansa con alternative
    """
    expanded = {}
    
    for role in ["lead", "pad", "bass"]:
        if role not in style_instruments:
            continue
        
        instrument = style_instruments[role]
        
        if isinstance(instrument, list):
            # Già una lista di alternative
            expanded[role] = instrument
            expanded[f"{role}_current"] = instrument[0]
        else:
            # Singolo strumento - aggiungi alternative dalla categoria
            expanded[role] = [instrument]
            expanded[f"{role}_current"] = instrument
            
            # Aggiungi alternative basate sul tipo di strumento
            if "lead" in instrument.lower() or "square" in instrument.lower() or "sawtooth" in instrument.lower():
                expanded[role].extend(INSTRUMENT_ALTERNATIVES["lead"]["synth"][:3])
            elif "brass" in instrument.lower():
                expanded[role].extend(INSTRUMENT_ALTERNATIVES["lead"]["brass"][:2])
            elif "guitar" in instrument.lower():
                expanded[role].extend(INSTRUMENT_ALTERNATIVES["lead"]["guitar"][:2])
            elif "piano" in instrument.lower() or "electric piano" in instrument.lower():
                expanded[role].extend(INSTRUMENT_ALTERNATIVES["lead"]["keys"][:2])
            elif "pad" in instrument.lower():
                if "choir" in instrument.lower():
                    expanded[role].extend(INSTRUMENT_ALTERNATIVES["pad"]["choir"][:2])
                elif "warm" in instrument.lower() or "new age" in instrument.lower():
                    expanded[role].extend(INSTRUMENT_ALTERNATIVES["pad"]["soft"][:2])
                else:
                    expanded[role].extend(INSTRUMENT_ALTERNATIVES["pad"]["synth"][:2])
            elif "bass" in instrument.lower():
                if "slap" in instrument.lower():
                    expanded[role].extend(INSTRUMENT_ALTERNATIVES["bass"]["slap"])
                elif "synth" in instrument.lower():
                    expanded[role].extend(INSTRUMENT_ALTERNATIVES["bass"]["synth"])
                else:
                    expanded[role].extend(INSTRUMENT_ALTERNATIVES["bass"]["electric"][:2])
    
    return expanded


def select_instrument_for_role(role, style_instruments, use_random=False):
    """
    Seleziona uno strumento per un ruolo specifico.
    
    Args:
        role: Ruolo ("lead", "pad", "bass")
        style_instruments: Configurazione strumenti dello stile
        use_random: Se True, seleziona casualmente dalle alternative
    
    Returns:
        str: Nome strumento GM selezionato
    """
    if not style_instruments or role not in style_instruments:
        return select_random_instrument(role)
    
    instrument_config = style_instruments[role]
    
    if isinstance(instrument_config, list):
        if use_random:
            return random.choice(instrument_config)
        return instrument_config[0]
    
    return instrument_config