STYLE_LIBRARY = {

    # ───────── HIP HOP / URBAN ─────────

    "trap": {
        "bpm_range": (130, 160),
        "drum_density": 0.8,
        "swing": 0.1,
        "patterns": {
            "kick":  [1,0,0,1,0,0,1,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [1]*16
        },
        # Musical parameters
        "scale_type": "harmonic_minor",
        "chord_complexity": 0.3,  # 0=simple triads, 1=complex extensions
        "bass_pattern": "syncopated",
        "melody_density": 0.4,
        "typical_progressions": [[0, 3, 4], [0, 4, 3], [0, 3]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 1 (new age)",
            "bass": "Electric Bass (finger)"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 4, "intensity": 0.2},
            {"type": "verse", "bars": 8, "intensity": 0.5},
            {"type": "chorus", "bars": 8, "intensity": 0.8},
            {"type": "verse", "bars": 8, "intensity": 0.6},
            {"type": "chorus", "bars": 8, "intensity": 0.9},
            {"type": "outro", "bars": 4, "intensity": 0.3}
        ]
    },

    "drill": {
        "bpm_range": (130, 145),
        "drum_density": 0.85,
        "swing": 0.2,
        "patterns": {
            "kick":  [1,0,1,0,0,1,0,1],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [1]*16
        },
        "scale_type": "harmonic_minor",
        "chord_complexity": 0.2,
        "bass_pattern": "sliding",
        "melody_density": 0.3,
        "typical_progressions": [[0, 3], [0, 4, 3]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 5 (bowed)",
            "bass": "Electric Bass (finger)"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 4, "intensity": 0.3},
            {"type": "verse", "bars": 8, "intensity": 0.6},
            {"type": "chorus", "bars": 8, "intensity": 0.9},
            {"type": "verse", "bars": 8, "intensity": 0.7},
            {"type": "chorus", "bars": 8, "intensity": 1.0}
        ]
    },

    "boom_bap": {
        "bpm_range": (80, 100),
        "drum_density": 0.6,
        "swing": 0.35,
        "patterns": {
            "kick":  [1,0,0,1,0,0,1,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [1,0]*8
        },
        "scale_type": "natural_minor",
        "chord_complexity": 0.5,
        "bass_pattern": "walking",
        "melody_density": 0.5,
        "typical_progressions": [[0, 3, 4, 3], [0, 5, 3, 4], [0, 1, 4, 3]],
        "instruments": {
            "lead": "Electric Piano 1",
            "pad": "String Ensemble 1",
            "bass": "Electric Bass (finger)"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 4, "intensity": 0.3},
            {"type": "verse", "bars": 16, "intensity": 0.6},
            {"type": "chorus", "bars": 8, "intensity": 0.8},
            {"type": "verse", "bars": 16, "intensity": 0.7},
            {"type": "chorus", "bars": 8, "intensity": 0.9},
            {"type": "outro", "bars": 4, "intensity": 0.4}
        ]
    },

    "lofi": {
        "bpm_range": (65, 90),
        "drum_density": 0.45,
        "swing": 0.4,
        "patterns": {
            "kick":  [1,0,0,0,1,0,0,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [1,0]*8
        },
        "scale_type": "major",
        "chord_complexity": 0.7,
        "bass_pattern": "simple",
        "melody_density": 0.3,
        "typical_progressions": [[0, 5, 3, 4], [0, 3, 5, 4], [0, 2, 5, 3]],
        "instruments": {
            "lead": "Electric Piano 1",
            "pad": "Pad 1 (new age)",
            "bass": "Electric Bass (finger)"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.2},
            {"type": "verse", "bars": 16, "intensity": 0.4},
            {"type": "chorus", "bars": 8, "intensity": 0.6},
            {"type": "verse", "bars": 16, "intensity": 0.5},
            {"type": "chorus", "bars": 8, "intensity": 0.7},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    # ───────── CLUB / ELECTRONIC ─────────

    "house": {
        "bpm_range": (118, 130),
        "drum_density": 0.8,
        "swing": 0.05,
        "patterns": {
            "kick":  [1,0,0,0]*4,
            "snare": [0]*16,
            "hihat": [0,1]*8
        },
        "scale_type": "minor",
        "chord_complexity": 0.4,
        "bass_pattern": "four_on_floor",
        "melody_density": 0.5,
        "typical_progressions": [[0, 3, 4], [0, 5, 3], [0, 3]],
        "instruments": {
            "lead": "Synth Brass 1",
            "pad": "Pad 1 (new age)",
            "bass": "Synth Bass 1"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.2},
            {"type": "build", "bars": 8, "intensity": 0.5},
            {"type": "drop", "bars": 16, "intensity": 0.9},
            {"type": "break", "bars": 8, "intensity": 0.4},
            {"type": "build", "bars": 8, "intensity": 0.6},
            {"type": "drop", "bars": 16, "intensity": 1.0},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    "deep_house": {
        "bpm_range": (118, 122),
        "drum_density": 0.6,
        "swing": 0.15,
        "patterns": {
            "kick":  [1,0,0,0]*4,
            "snare": [0]*16,
            "hihat": [0,1,1,0]*4
        },
        "scale_type": "dorian",
        "chord_complexity": 0.6,
        "bass_pattern": "groovy",
        "melody_density": 0.4,
        "typical_progressions": [[0, 3, 5], [0, 5, 3, 6], [0, 2, 5, 3]],
        "instruments": {
            "lead": "Synth Strings 1",
            "pad": "Pad 2 (warm)",
            "bass": "Synth Bass 1"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.2},
            {"type": "verse", "bars": 16, "intensity": 0.5},
            {"type": "chorus", "bars": 16, "intensity": 0.8},
            {"type": "verse", "bars": 16, "intensity": 0.6},
            {"type": "chorus", "bars": 16, "intensity": 0.9},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    "techno": {
        "bpm_range": (125, 140),
        "drum_density": 0.9,
        "swing": 0.0,
        "patterns": {
            "kick":  [1,0,0,0]*4,
            "snare": [0]*16,
            "hihat": [0,1]*8
        },
        "scale_type": "phrygian",
        "chord_complexity": 0.2,
        "bass_pattern": "driving",
        "melody_density": 0.3,
        "typical_progressions": [[0], [0, 3], [0, 6]],
        "instruments": {
            "lead": "Lead 6 (voice)",
            "pad": "Pad 4 (choir)",
            "bass": "Synth Bass 1"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 16, "intensity": 0.2},
            {"type": "build", "bars": 8, "intensity": 0.5},
            {"type": "drop", "bars": 32, "intensity": 0.9},
            {"type": "break", "bars": 8, "intensity": 0.3},
            {"type": "build", "bars": 8, "intensity": 0.6},
            {"type": "drop", "bars": 32, "intensity": 1.0},
            {"type": "outro", "bars": 16, "intensity": 0.2}
        ]
    },

    "minimal_techno": {
        "bpm_range": (120, 128),
        "drum_density": 0.4,
        "swing": 0.0,
        "patterns": {
            "kick":  [1,0,0,0]*4,
            "snare": [0]*16,
            "hihat": [0,0,1,0]*4
        },
        "scale_type": "locrian",
        "chord_complexity": 0.1,
        "bass_pattern": "minimal",
        "melody_density": 0.2,
        "typical_progressions": [[0], [0, 6]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 8 (sweep)",
            "bass": "Synth Bass 1"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 16, "intensity": 0.1},
            {"type": "build", "bars": 16, "intensity": 0.4},
            {"type": "drop", "bars": 32, "intensity": 0.7},
            {"type": "break", "bars": 16, "intensity": 0.2},
            {"type": "build", "bars": 16, "intensity": 0.5},
            {"type": "drop", "bars": 32, "intensity": 0.8},
            {"type": "outro", "bars": 16, "intensity": 0.1}
        ]
    },

    "dubstep": {
        "bpm_range": (135, 145),
        "drum_density": 0.7,
        "swing": 0.0,
        "patterns": {
            "kick":  [1,0,0,0,0,1,0,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [1,0,0,0]*4
        },
        "scale_type": "harmonic_minor",
        "chord_complexity": 0.3,
        "bass_pattern": "wobble",
        "melody_density": 0.4,
        "typical_progressions": [[0, 3], [0, 4, 3]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 5 (bowed)",
            "bass": "Synth Bass 2"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.3},
            {"type": "build", "bars": 8, "intensity": 0.6},
            {"type": "drop", "bars": 16, "intensity": 0.95},
            {"type": "break", "bars": 8, "intensity": 0.3},
            {"type": "build", "bars": 8, "intensity": 0.7},
            {"type": "drop", "bars": 16, "intensity": 1.0},
            {"type": "outro", "bars": 8, "intensity": 0.2}
        ]
    },

    "dnb": {
        "bpm_range": (165, 180),
        "drum_density": 0.9,
        "swing": 0.0,
        "patterns": {
            "kick":  [1,0,0,1,0,0,1,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [1]*16
        },
        "scale_type": "natural_minor",
        "chord_complexity": 0.3,
        "bass_pattern": "rolling",
        "melody_density": 0.5,
        "typical_progressions": [[0, 3, 4], [0, 5, 3]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 1 (new age)",
            "bass": "Synth Bass 1"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.3},
            {"type": "verse", "bars": 16, "intensity": 0.6},
            {"type": "chorus", "bars": 16, "intensity": 0.9},
            {"type": "verse", "bars": 16, "intensity": 0.7},
            {"type": "chorus", "bars": 16, "intensity": 1.0},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    # ───────── CINEMATIC / ATMOS ─────────

    "ambient": {
        "bpm_range": (40, 80),
        "drum_density": 0.1,
        "swing": 0.0,
        "patterns": {},
        "scale_type": "major",
        "chord_complexity": 0.8,
        "bass_pattern": "drone",
        "melody_density": 0.1,
        "typical_progressions": [[0, 5, 3], [0, 2, 5], [0, 6, 3, 5]],
        "instruments": {
            "lead": "Pad 1 (new age)",
            "pad": "Pad 4 (choir)",
            "bass": "Pad 5 (bowed)"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 16, "intensity": 0.1},
            {"type": "verse", "bars": 32, "intensity": 0.3},
            {"type": "chorus", "bars": 16, "intensity": 0.5},
            {"type": "verse", "bars": 32, "intensity": 0.4},
            {"type": "chorus", "bars": 16, "intensity": 0.6},
            {"type": "outro", "bars": 16, "intensity": 0.2}
        ]
    },

    "cinematic": {
        "bpm_range": (60, 100),
        "drum_density": 0.3,
        "swing": 0.0,
        "patterns": {
            "kick":  [1,0,0,0,0,0,0,0],
            "snare": [0]*16
        },
        "scale_type": "harmonic_minor",
        "chord_complexity": 0.7,
        "bass_pattern": "orchestral",
        "melody_density": 0.4,
        "typical_progressions": [[0, 3, 5, 6], [0, 5, 3, 4], [0, 2, 5, 1]],
        "instruments": {
            "lead": "Orchestra Strings",
            "pad": "Pad 4 (choir)",
            "bass": "Pad 5 (bowed)"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.2},
            {"type": "verse", "bars": 16, "intensity": 0.4},
            {"type": "build", "bars": 8, "intensity": 0.7},
            {"type": "chorus", "bars": 16, "intensity": 0.9},
            {"type": "verse", "bars": 16, "intensity": 0.5},
            {"type": "build", "bars": 8, "intensity": 0.8},
            {"type": "chorus", "bars": 16, "intensity": 1.0},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    "downtempo": {
        "bpm_range": (80, 110),
        "drum_density": 0.4,
        "swing": 0.2,
        "patterns": {
            "kick":  [1,0,0,1,0,0,0,0],
            "snare": [0,0,1,0,0,0,1,0]
        },
        "scale_type": "dorian",
        "chord_complexity": 0.6,
        "bass_pattern": "groovy",
        "melody_density": 0.4,
        "typical_progressions": [[0, 5, 3, 4], [0, 3, 5], [0, 2, 5, 3]],
        "instruments": {
            "lead": "Electric Piano 1",
            "pad": "Pad 2 (warm)",
            "bass": "Electric Bass (finger)"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.2},
            {"type": "verse", "bars": 16, "intensity": 0.4},
            {"type": "chorus", "bars": 8, "intensity": 0.7},
            {"type": "verse", "bars": 16, "intensity": 0.5},
            {"type": "chorus", "bars": 8, "intensity": 0.8},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    # ───────── BAND / ACOUSTIC ─────────

    "rock": {
        "bpm_range": (90, 140),
        "drum_density": 0.7,
        "swing": 0.0,
        "patterns": {
            "kick":  [1,0,0,0,1,0,0,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [1,0]*8
        },
        "scale_type": "major",
        "chord_complexity": 0.3,
        "bass_pattern": "driving",
        "melody_density": 0.6,
        "typical_progressions": [[0, 4, 5, 3], [0, 5, 3, 4], [0, 4, 3, 5]],
        "instruments": {
            "lead": "Electric Guitar (clean)",
            "pad": "String Ensemble 1",
            "bass": "Electric Bass (finger)"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 4, "intensity": 0.4},
            {"type": "verse", "bars": 8, "intensity": 0.5},
            {"type": "chorus", "bars": 8, "intensity": 0.8},
            {"type": "verse", "bars": 8, "intensity": 0.6},
            {"type": "chorus", "bars": 8, "intensity": 0.9},
            {"type": "bridge", "bars": 8, "intensity": 0.7},
            {"type": "chorus", "bars": 8, "intensity": 1.0},
            {"type": "outro", "bars": 4, "intensity": 0.5}
        ]
    },

    "funk": {
        "bpm_range": (95, 120),
        "drum_density": 0.75,
        "swing": 0.3,
        "patterns": {
            "kick":  [1,0,0,1,0,1,0,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [1,1,0,1]*4
        },
        "scale_type": "mixolydian",
        "chord_complexity": 0.5,
        "bass_pattern": "slap",
        "melody_density": 0.6,
        "typical_progressions": [[0, 3], [0, 4, 3], [0, 3, 4]],
        "instruments": {
            "lead": "Electric Guitar (clean)",
            "pad": "Electric Piano 1",
            "bass": "Electric Bass (finger)"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 4, "intensity": 0.4},
            {"type": "verse", "bars": 8, "intensity": 0.6},
            {"type": "chorus", "bars": 8, "intensity": 0.8},
            {"type": "verse", "bars": 8, "intensity": 0.7},
            {"type": "chorus", "bars": 8, "intensity": 0.9},
            {"type": "bridge", "bars": 8, "intensity": 0.7},
            {"type": "chorus", "bars": 8, "intensity": 1.0},
            {"type": "outro", "bars": 4, "intensity": 0.5}
        ]
    },

    "jazz": {
        "bpm_range": (90, 140),
        "drum_density": 0.5,
        "swing": 0.45,
        "patterns": {
            "kick":  [0]*16,
            "snare": [0]*16,
            "hihat": [0,1]*8
        },
        "scale_type": "dorian",
        "chord_complexity": 0.9,
        "bass_pattern": "walking",
        "melody_density": 0.7,
        "typical_progressions": [[0, 1, 4, 3], [2, 5, 1, 4], [5, 1, 4, 0], [1, 4, 0]],
        "instruments": {
            "lead": "Acoustic Grand Piano",
            "pad": "String Ensemble 1",
            "bass": "Acoustic Bass"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 4, "intensity": 0.3},
            {"type": "verse", "bars": 16, "intensity": 0.5},
            {"type": "chorus", "bars": 16, "intensity": 0.7},
            {"type": "solo", "bars": 16, "intensity": 0.8},
            {"type": "verse", "bars": 16, "intensity": 0.6},
            {"type": "chorus", "bars": 16, "intensity": 0.9},
            {"type": "outro", "bars": 4, "intensity": 0.4}
        ]
    },

    # ───────── SYNTH / RETRO / ELECTRONIC ─────────

    "synthpop": {
        "bpm_range": (100, 120),
        "drum_density": 0.65,
        "swing": 0.05,
        "patterns": {
            "kick":  [1,0,0,0,1,0,0,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [0,1]*8
        },
        "scale_type": "major",
        "chord_complexity": 0.4,
        "bass_pattern": "arpeggiated",
        "melody_density": 0.6,
        "typical_progressions": [[0, 4, 5, 3], [0, 5, 3, 4], [0, 3, 5, 4]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 1 (new age)",
            "bass": "Synth Bass 1"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 4, "intensity": 0.3},
            {"type": "verse", "bars": 8, "intensity": 0.5},
            {"type": "chorus", "bars": 8, "intensity": 0.8},
            {"type": "verse", "bars": 8, "intensity": 0.6},
            {"type": "chorus", "bars": 8, "intensity": 0.9},
            {"type": "bridge", "bars": 8, "intensity": 0.7},
            {"type": "chorus", "bars": 8, "intensity": 1.0},
            {"type": "outro", "bars": 4, "intensity": 0.4}
        ]
    },

    "synthwave": {
        "bpm_range": (85, 110),
        "drum_density": 0.55,
        "swing": 0.0,
        "patterns": {
            "kick":  [1,0,0,0,1,0,0,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [0,0,1,0]*4
        },
        "scale_type": "natural_minor",
        "chord_complexity": 0.5,
        "bass_pattern": "arpeggiated",
        "melody_density": 0.5,
        "typical_progressions": [[0, 3, 5, 4], [0, 5, 3, 4], [0, 3, 4, 5]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 1 (new age)",
            "bass": "Synth Bass 2"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.2},
            {"type": "verse", "bars": 16, "intensity": 0.5},
            {"type": "chorus", "bars": 16, "intensity": 0.8},
            {"type": "verse", "bars": 16, "intensity": 0.6},
            {"type": "chorus", "bars": 16, "intensity": 0.9},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    "retrowave": {
        "bpm_range": (90, 115),
        "drum_density": 0.6,
        "swing": 0.0,
        "patterns": {
            "kick":  [1,0,0,0,0,0,0,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [0,1,0,1]*4
        },
        "scale_type": "natural_minor",
        "chord_complexity": 0.4,
        "bass_pattern": "driving",
        "melody_density": 0.5,
        "typical_progressions": [[0, 3, 5, 4], [0, 5, 3], [0, 3, 4]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 1 (new age)",
            "bass": "Synth Bass 1"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.3},
            {"type": "verse", "bars": 16, "intensity": 0.5},
            {"type": "chorus", "bars": 16, "intensity": 0.8},
            {"type": "verse", "bars": 16, "intensity": 0.6},
            {"type": "chorus", "bars": 16, "intensity": 0.9},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    "outrun": {
        "bpm_range": (95, 125),
        "drum_density": 0.7,
        "swing": 0.0,
        "patterns": {
            "kick":  [1,0,0,0,1,0,1,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [1,0,1,0]*4
        },
        "scale_type": "harmonic_minor",
        "chord_complexity": 0.4,
        "bass_pattern": "driving",
        "melody_density": 0.6,
        "typical_progressions": [[0, 3, 5, 4], [0, 5, 3, 4], [0, 3, 4, 5]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 1 (new age)",
            "bass": "Synth Bass 2"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.3},
            {"type": "verse", "bars": 16, "intensity": 0.5},
            {"type": "chorus", "bars": 16, "intensity": 0.8},
            {"type": "verse", "bars": 16, "intensity": 0.6},
            {"type": "chorus", "bars": 16, "intensity": 0.9},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    "darkwave": {
        "bpm_range": (90, 115),
        "drum_density": 0.5,
        "swing": 0.0,
        "patterns": {
            "kick":  [1,0,0,0,0,0,0,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [0,0,1,0]*4
        },
        "scale_type": "phrygian",
        "chord_complexity": 0.5,
        "bass_pattern": "driving",
        "melody_density": 0.4,
        "typical_progressions": [[0, 1, 3], [0, 3, 1], [0, 6, 3]],
        "instruments": {
            "lead": "Lead 6 (voice)",
            "pad": "Pad 4 (choir)",
            "bass": "Synth Bass 2"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.2},
            {"type": "verse", "bars": 16, "intensity": 0.5},
            {"type": "chorus", "bars": 16, "intensity": 0.8},
            {"type": "verse", "bars": 16, "intensity": 0.6},
            {"type": "chorus", "bars": 16, "intensity": 0.9},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    "ebm": {  # Electronic Body Music
        "bpm_range": (120, 140),
        "drum_density": 0.85,
        "swing": 0.0,
        "patterns": {
            "kick":  [1,0,0,0]*4,
            "snare": [0,0,1,0]*4,
            "hihat": [1,0]*8
        },
        "scale_type": "phrygian",
        "chord_complexity": 0.3,
        "bass_pattern": "driving",
        "melody_density": 0.5,
        "typical_progressions": [[0, 3], [0, 1, 3], [0, 6]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 5 (bowed)",
            "bass": "Synth Bass 1"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.3},
            {"type": "verse", "bars": 16, "intensity": 0.6},
            {"type": "chorus", "bars": 16, "intensity": 0.9},
            {"type": "verse", "bars": 16, "intensity": 0.7},
            {"type": "chorus", "bars": 16, "intensity": 1.0},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    "electro": {  # electro-funk
        "bpm_range": (110, 130),
        "drum_density": 0.75,
        "swing": 0.1,
        "patterns": {
            "kick":  [1,0,1,0,0,1,0,0],
            "snare": [0,0,1,0,0,0,1,0],
            "hihat": [1,1,0,1]*4
        },
        "scale_type": "mixolydian",
        "chord_complexity": 0.5,
        "bass_pattern": "funky",
        "melody_density": 0.6,
        "typical_progressions": [[0, 3, 4], [0, 4, 3], [0, 3]],
        "instruments": {
            "lead": "Electric Piano 1",
            "pad": "Pad 1 (new age)",
            "bass": "Electric Bass (finger)"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 4, "intensity": 0.3},
            {"type": "verse", "bars": 8, "intensity": 0.5},
            {"type": "chorus", "bars": 8, "intensity": 0.8},
            {"type": "verse", "bars": 8, "intensity": 0.6},
            {"type": "chorus", "bars": 8, "intensity": 0.9},
            {"type": "outro", "bars": 4, "intensity": 0.4}
        ]
    },

    "idm": {
        "bpm_range": (90, 160),
        "drum_density": 0.6,
        "swing": 0.2,
        "patterns": {
            "kick":  [1,0,0,1,0,0,1,0],
            "snare": [0,1,0,0,1,0,0,1],
            "hihat": [1,0,1,1,0,1,0,0]
        },
        "scale_type": "chromatic",
        "chord_complexity": 0.7,
        "bass_pattern": "experimental",
        "melody_density": 0.5,
        "typical_progressions": [[0, 2, 6, 5], [0, 5, 2, 3], [6, 3, 0]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 8 (sweep)",
            "bass": "Synth Bass 2"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.3},
            {"type": "verse", "bars": 16, "intensity": 0.5},
            {"type": "chorus", "bars": 16, "intensity": 0.8},
            {"type": "verse", "bars": 16, "intensity": 0.6},
            {"type": "chorus", "bars": 16, "intensity": 0.9},
            {"type": "outro", "bars": 8, "intensity": 0.3}
        ]
    },

    "glitch": {
        "bpm_range": (70, 130),
        "drum_density": 0.4,
        "swing": 0.25,
        "patterns": {
            "kick":  [1,0,0,0,0,1,0,0],
            "snare": [0,0,1,0,0,0,0,1],
            "hihat": [1,0,0,1,0,1,0,1]
        },
        "scale_type": "whole_tone",
        "chord_complexity": 0.6,
        "bass_pattern": "glitchy",
        "melody_density": 0.4,
        "typical_progressions": [[0, 2, 4], [0, 4, 2], [0, 6]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 8 (sweep)",
            "bass": "Synth Bass 2"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 8, "intensity": 0.2},
            {"type": "verse", "bars": 16, "intensity": 0.4},
            {"type": "chorus", "bars": 16, "intensity": 0.7},
            {"type": "verse", "bars": 16, "intensity": 0.5},
            {"type": "chorus", "bars": 16, "intensity": 0.8},
            {"type": "outro", "bars": 8, "intensity": 0.2}
        ]
    },

    "electronic_pop": {
        "bpm_range": (100, 128),
        "drum_density": 0.7,
        "swing": 0.05,
        "patterns": {
            "kick":  [1,0,0,0]*4,
            "snare": [0,0,1,0]*4,
            "hihat": [0,1]*8
        },
        "scale_type": "major",
        "chord_complexity": 0.4,
        "bass_pattern": "simple",
        "melody_density": 0.6,
        "typical_progressions": [[0, 4, 5, 3], [0, 5, 3, 4], [0, 3, 5, 4]],
        "instruments": {
            "lead": "Lead 1 (square)",
            "pad": "Pad 1 (new age)",
            "bass": "Synth Bass 1"
        },
        "arrangement_template": [
            {"type": "intro", "bars": 4, "intensity": 0.3},
            {"type": "verse", "bars": 8, "intensity": 0.5},
            {"type": "pre_chorus", "bars": 4, "intensity": 0.7},
            {"type": "chorus", "bars": 8, "intensity": 0.9},
            {"type": "verse", "bars": 8, "intensity": 0.6},
            {"type": "pre_chorus", "bars": 4, "intensity": 0.7},
            {"type": "chorus", "bars": 8, "intensity": 1.0},
            {"type": "outro", "bars": 4, "intensity": 0.4}
        ]
    }
}

def get_style(style_name):
    """Retrieve a style configuration by name."""
    return STYLE_LIBRARY.get(style_name)

def get_style_bpm(style_name):
    """Get a random BPM within the style's range."""
    import random
    style = STYLE_LIBRARY.get(style_name)
    if not style:
        return 120
    low, high = style["bpm_range"]
    return random.randint(low, high)

def get_style_list():
    """Return a list of all available style names."""
    return list(STYLE_LIBRARY.keys())