# ============================================================================
# DRUM MIDI NOTES
# ============================================================================
DRUM_NOTES = {
    "kick": 36,
    "snare": 38,
    "hihat_closed": 42,
    "hihat_open": 46,
    "hihat_pedal": 44,
    "ride": 51,
    "ride_bell": 52,
    "crash": 49,
    "crash_2": 57,
    "clap": 39,
    "tom_high": 50,
    "tom_mid": 47,
    "tom_low": 45,
    "cowbell": 56,
    "click": 75,
}

# ============================================================================
# BASS THEORY CONFIGURATIONS
# ============================================================================
# These define how bass lines should be constructed for each style
# using music theory awareness

BASS_THEORY_CONFIGS = {
    # ───────── HIP HOP / URBAN ─────────
    "trap": {
        "approach": "chord_tones",  # Target chord tones on strong beats
        "scale_preference": ["root", "fifth", "octave", "minor_third"],  # Preferred intervals
        "rhythmic_density": 0.4,  # Notes per beat (relative)
        "octave_range": (1, 2),  # Octave range (C1-C3 typically)
        "note_lengths": ["eighth", "quarter", "dotted_quarter"],
        "syncopation": 0.6,  # How much to emphasize off-beats
        "approach_patterns": ["chromatic_below", "diatonic_above", "leap"],
        "slide_frequency": 0.3,  # How often to slide between notes
        "variation_on_repeat": True,  # Vary pattern each repetition
    },
    "drill": {
        "approach": "root_fifth",
        "scale_preference": ["root", "fifth", "octave"],
        "rhythmic_density": 0.35,
        "octave_range": (1, 2),
        "note_lengths": ["quarter", "dotted_quarter", "half"],
        "syncopation": 0.7,
        "approach_patterns": ["chromatic_below", "slide"],
        "slide_frequency": 0.5,
        "variation_on_repeat": True,
    },
    "boom_bap": {
        "approach": "walking",
        "scale_preference": ["root", "second", "third", "fifth", "sixth"],
        "rhythmic_density": 0.7,
        "octave_range": (1, 2),
        "note_lengths": ["quarter", "eighth"],
        "syncopation": 0.4,
        "approach_patterns": ["diatonic_below", "diatonic_above", "chromatic_below"],
        "slide_frequency": 0.1,
        "variation_on_repeat": True,
    },
    "lofi": {
        "approach": "simple",
        "scale_preference": ["root", "fifth", "octave"],
        "rhythmic_density": 0.3,
        "octave_range": (1, 2),
        "note_lengths": ["half", "dotted_half", "whole"],
        "syncopation": 0.2,
        "approach_patterns": ["direct"],
        "slide_frequency": 0.05,
        "variation_on_repeat": False,
    },

    # ───────── CLUB / ELECTRONIC ─────────
    "house": {
        "approach": "four_on_floor",
        "scale_preference": ["root", "octave", "fifth"],
        "rhythmic_density": 0.8,
        "octave_range": (1, 2),
        "note_lengths": ["quarter"],
        "syncopation": 0.1,
        "approach_patterns": ["direct", "octave_leap"],
        "slide_frequency": 0.0,
        "variation_on_repeat": False,
    },
    "deep_house": {
        "approach": "groovy",
        "scale_preference": ["root", "fifth", "seventh", "ninth"],
        "rhythmic_density": 0.5,
        "octave_range": (1, 2),
        "note_lengths": ["eighth", "quarter", "dotted_eighth"],
        "syncopation": 0.5,
        "approach_patterns": ["chromatic_below", "diatonic_above"],
        "slide_frequency": 0.15,
        "variation_on_repeat": True,
    },
    "techno": {
        "approach": "driving",
        "scale_preference": ["root", "octave"],
        "rhythmic_density": 0.9,
        "octave_range": (1, 2),
        "note_lengths": ["eighth", "quarter"],
        "syncopation": 0.05,
        "approach_patterns": ["direct"],
        "slide_frequency": 0.0,
        "variation_on_repeat": False,
    },
    "minimal_techno": {
        "approach": "minimal",
        "scale_preference": ["root"],
        "rhythmic_density": 0.2,
        "octave_range": (1, 2),
        "note_lengths": ["whole", "dotted_half"],
        "syncopation": 0.0,
        "approach_patterns": ["direct"],
        "slide_frequency": 0.0,
        "variation_on_repeat": False,
    },
    "dubstep": {
        "approach": "wobble",
        "scale_preference": ["root", "fifth", "minor_third"],
        "rhythmic_density": 0.6,
        "octave_range": (0, 2),  # Sub-bass range
        "note_lengths": ["quarter", "half"],
        "syncopation": 0.4,
        "approach_patterns": ["direct", "octave_leap"],
        "slide_frequency": 0.2,
        "variation_on_repeat": True,
        "wobble_rate": 0.3,  # LFO-like pitch modulation
    },
    "dnb": {
        "approach": "rolling",
        "scale_preference": ["root", "fifth", "octave", "minor_seventh"],
        "rhythmic_density": 0.8,
        "octave_range": (1, 2),
        "note_lengths": ["eighth", "sixteenth"],
        "syncopation": 0.6,
        "approach_patterns": ["diatonic_below", "chromatic_below"],
        "slide_frequency": 0.2,
        "variation_on_repeat": True,
    },

    # ───────── CINEMATIC / ATMOS ─────────
    "ambient": {
        "approach": "drone",
        "scale_preference": ["root", "fifth", "octave"],
        "rhythmic_density": 0.1,
        "octave_range": (0, 1),
        "note_lengths": ["whole", "double_whole"],
        "syncopation": 0.0,
        "approach_patterns": ["direct"],
        "slide_frequency": 0.0,
        "variation_on_repeat": False,
    },
    "cinematic": {
        "approach": "orchestral",
        "scale_preference": ["root", "fifth", "octave", "third"],
        "rhythmic_density": 0.3,
        "octave_range": (0, 2),
        "note_lengths": ["half", "whole", "dotted_half"],
        "syncopation": 0.1,
        "approach_patterns": ["direct", "leap"],
        "slide_frequency": 0.05,
        "variation_on_repeat": False,
    },
    "downtempo": {
        "approach": "groovy",
        "scale_preference": ["root", "fifth", "seventh"],
        "rhythmic_density": 0.4,
        "octave_range": (1, 2),
        "note_lengths": ["quarter", "half"],
        "syncopation": 0.4,
        "approach_patterns": ["chromatic_below", "diatonic_above"],
        "slide_frequency": 0.1,
        "variation_on_repeat": True,
    },

    # ───────── BAND / ACOUSTIC ─────────
    "rock": {
        "approach": "driving",
        "scale_preference": ["root", "fifth", "octave", "third"],
        "rhythmic_density": 0.7,
        "octave_range": (1, 2),
        "note_lengths": ["eighth", "quarter"],
        "syncopation": 0.2,
        "approach_patterns": ["direct", "octave_leap"],
        "slide_frequency": 0.05,
        "variation_on_repeat": True,
    },
    "funk": {
        "approach": "slap",
        "scale_preference": ["root", "fifth", "seventh", "ninth", "octave"],
        "rhythmic_density": 0.8,
        "octave_range": (1, 2),
        "note_lengths": ["eighth", "sixteenth", "dotted_sixteenth"],
        "syncopation": 0.8,
        "approach_patterns": ["chromatic_below", "octave_leap", "slap_pop"],
        "slide_frequency": 0.3,
        "variation_on_repeat": True,
    },
    "jazz": {
        "approach": "walking",
        "scale_preference": ["root", "second", "third", "fourth", "fifth", "sixth", "seventh"],
        "rhythmic_density": 0.9,
        "octave_range": (1, 2),
        "note_lengths": ["quarter"],
        "syncopation": 0.3,
        "approach_patterns": ["diatonic_below", "diatonic_above", "chromatic_below", "chromatic_above"],
        "slide_frequency": 0.0,
        "variation_on_repeat": True,
    },

    # ───────── SYNTH / RETRO / ELECTRONIC ─────────
    "synthpop": {
        "approach": "arpeggiated",
        "scale_preference": ["root", "third", "fifth", "octave"],
        "rhythmic_density": 0.7,
        "octave_range": (1, 2),
        "note_lengths": ["eighth", "sixteenth"],
        "syncopation": 0.2,
        "approach_patterns": ["arpeggio_up", "arpeggio_down"],
        "slide_frequency": 0.0,
        "variation_on_repeat": False,
    },
    "synthwave": {
        "approach": "arpeggiated",
        "scale_preference": ["root", "third", "fifth", "octave"],
        "rhythmic_density": 0.6,
        "octave_range": (1, 2),
        "note_lengths": ["eighth", "quarter"],
        "syncopation": 0.15,
        "approach_patterns": ["arpeggio_up", "arpeggio_down"],
        "slide_frequency": 0.0,
        "variation_on_repeat": False,
    },
    "retrowave": {
        "approach": "driving",
        "scale_preference": ["root", "fifth", "octave"],
        "rhythmic_density": 0.6,
        "octave_range": (1, 2),
        "note_lengths": ["eighth", "quarter"],
        "syncopation": 0.2,
        "approach_patterns": ["direct", "octave_leap"],
        "slide_frequency": 0.05,
        "variation_on_repeat": True,
    },
    "outrun": {
        "approach": "driving",
        "scale_preference": ["root", "fifth", "octave", "minor_third"],
        "rhythmic_density": 0.7,
        "octave_range": (1, 2),
        "note_lengths": ["eighth", "quarter"],
        "syncopation": 0.25,
        "approach_patterns": ["direct", "octave_leap"],
        "slide_frequency": 0.1,
        "variation_on_repeat": True,
    },
    "darkwave": {
        "approach": "driving",
        "scale_preference": ["root", "fifth", "octave"],
        "rhythmic_density": 0.5,
        "octave_range": (1, 2),
        "note_lengths": ["quarter", "half"],
        "syncopation": 0.1,
        "approach_patterns": ["direct"],
        "slide_frequency": 0.0,
        "variation_on_repeat": False,
    },
    "ebm": {
        "approach": "driving",
        "scale_preference": ["root", "fifth", "octave"],
        "rhythmic_density": 0.8,
        "octave_range": (1, 2),
        "note_lengths": ["eighth", "quarter"],
        "syncopation": 0.1,
        "approach_patterns": ["direct"],
        "slide_frequency": 0.0,
        "variation_on_repeat": False,
    },
    "electro": {
        "approach": "funky",
        "scale_preference": ["root", "fifth", "seventh", "ninth"],
        "rhythmic_density": 0.7,
        "octave_range": (1, 2),
        "note_lengths": ["eighth", "sixteenth"],
        "syncopation": 0.6,
        "approach_patterns": ["chromatic_below", "octave_leap"],
        "slide_frequency": 0.2,
        "variation_on_repeat": True,
    },
    "idm": {
        "approach": "experimental",
        "scale_preference": ["root", "minor_second", "tritone", "major_seventh"],
        "rhythmic_density": 0.5,
        "octave_range": (0, 3),
        "note_lengths": ["eighth", "quarter", "dotted_quarter", "half"],
        "syncopation": 0.7,
        "approach_patterns": ["chromatic_below", "leap", "random"],
        "slide_frequency": 0.3,
        "variation_on_repeat": True,
    },
    "glitch": {
        "approach": "glitchy",
        "scale_preference": ["root", "minor_second", "tritone"],
        "rhythmic_density": 0.4,
        "octave_range": (0, 3),
        "note_lengths": ["sixteenth", "eighth", "dotted_eighth"],
        "syncopation": 0.8,
        "approach_patterns": ["random", "leap"],
        "slide_frequency": 0.4,
        "variation_on_repeat": True,
    },
    "electronic_pop": {
        "approach": "simple",
        "scale_preference": ["root", "fifth", "octave"],
        "rhythmic_density": 0.5,
        "octave_range": (1, 2),
        "note_lengths": ["quarter", "half"],
        "syncopation": 0.2,
        "approach_patterns": ["direct"],
        "slide_frequency": 0.05,
        "variation_on_repeat": False,
    },
}

# ============================================================================
# DRUM STYLE CONFIGURATIONS
# ============================================================================
# Detailed drum patterns and behaviors per style

DRUM_STYLE_CONFIGS = {
    # ───────── HIP HOP / URBAN ─────────
    "trap": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            },
            "variation_1": {
                "kick":  [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            },
            "hihat_roll": {
                "kick":  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],  # Rolls
            },
        },
        "velocities": {
            "kick_base": 100,
            "snare_base": 95,
            "hihat_base": 60,
            "hihat_variation": 25,  # Range of variation
            "ghost_note_max": 40,
        },
        "humanization": {
            "timing_jitter": 0.02,  # Max timing deviation (in 16th notes)
            "velocity_jitter": 0.15,
            "swing_amount": 0.1,
        },
        "fills": {
            "frequency": 0.3,  # Probability of fill at phrase boundary
            "patterns": [
                {"kick": [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 "snare": [0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,0],
                 "hihat": [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]},
            ],
        },
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.7, "use_patterns": ["basic", "variation_1"]},
            "chorus": {"density_modifier": 1.0, "use_patterns": ["basic", "variation_1", "hihat_roll"]},
            "bridge": {"density_modifier": 0.6, "use_patterns": ["variation_1"]},
        },
    },
    "drill": {
        "patterns": {
            "basic": {
                "kick":  [1,0,1,0,0,1,0,0,0,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            },
            "slide_kick": {
                "kick":  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 110,
            "snare_base": 100,
            "hihat_base": 55,
            "hihat_variation": 30,
            "ghost_note_max": 35,
        },
        "humanization": {
            "timing_jitter": 0.03,
            "velocity_jitter": 0.2,
            "swing_amount": 0.2,
        },
        "fills": {
            "frequency": 0.25,
            "patterns": [
                {"kick": [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 "snare": [0,0,0,0,0,0,0,0,1,0,1,0,1,1,0,1],
                 "hihat": [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]},
            ],
        },
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.8, "use_patterns": ["basic", "slide_kick"]},
            "chorus": {"density_modifier": 1.0, "use_patterns": ["basic", "slide_kick"]},
        },
    },
    "boom_bap": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            },
            "break": {
                "kick":  [1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,1,0,0,1,0,0,1,0,1],
                "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 90,
            "snare_base": 95,
            "hihat_base": 70,
            "hihat_variation": 20,
            "ghost_note_max": 45,
        },
        "humanization": {
            "timing_jitter": 0.04,
            "velocity_jitter": 0.25,
            "swing_amount": 0.35,
        },
        "fills": {
            "frequency": 0.4,
            "patterns": [
                {"kick": [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 "snare": [0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,1],
                 "hihat": [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]},
            ],
        },
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.7, "use_patterns": ["basic", "break"]},
            "chorus": {"density_modifier": 0.9, "use_patterns": ["basic", "break"]},
        },
    },
    "lofi": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
            },
        },
        "velocities": {
            "kick_base": 70,
            "snare_base": 65,
            "hihat_base": 50,
            "hihat_variation": 15,
            "ghost_note_max": 30,
        },
        "humanization": {
            "timing_jitter": 0.05,
            "velocity_jitter": 0.3,
            "swing_amount": 0.4,
        },
        "fills": {
            "frequency": 0.15,
            "patterns": [],
        },
        "section_variations": {
            "intro": {"density_modifier": 0.4, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.7, "use_patterns": ["basic"]},
        },
    },

    # ───────── CLUB / ELECTRONIC ─────────
    "house": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                "hihat": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
                "clap":  [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
            },
            "open_hat": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                "hihat": [0,0,1,1,0,0,1,0,0,0,1,1,0,0,1,0],  # Open on offbeat
                "clap":  [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
            },
        },
        "velocities": {
            "kick_base": 110,
            "snare_base": 0,
            "hihat_base": 75,
            "hihat_variation": 15,
            "clap_base": 90,
            "ghost_note_max": 0,
        },
        "humanization": {
            "timing_jitter": 0.01,
            "velocity_jitter": 0.08,
            "swing_amount": 0.05,
        },
        "fills": {
            "frequency": 0.3,
            "patterns": [
                {"kick": [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                 "hihat": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,1],
                 "clap":  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 "crash": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]},
            ],
        },
        "section_variations": {
            "intro": {"density_modifier": 0.4, "use_patterns": ["basic"]},
            "build": {"density_modifier": 0.7, "use_patterns": ["basic", "open_hat"]},
            "drop": {"density_modifier": 1.0, "use_patterns": ["basic", "open_hat"]},
            "break": {"density_modifier": 0.3, "use_patterns": ["basic"]},
        },
    },
    "deep_house": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "hihat": [0,0,1,0,0,1,1,0,0,0,1,0,0,1,1,0],
                "clap":  [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
            },
        },
        "velocities": {
            "kick_base": 100,
            "hihat_base": 65,
            "hihat_variation": 20,
            "clap_base": 80,
        },
        "humanization": {
            "timing_jitter": 0.02,
            "velocity_jitter": 0.15,
            "swing_amount": 0.15,
        },
        "fills": {"frequency": 0.25, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.4, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.6, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.85, "use_patterns": ["basic"]},
        },
    },
    "techno": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "hihat": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
            },
            "accent": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,1,0],
                "hihat": [0,0,1,0,0,0,1,1,0,0,1,0,0,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 115,
            "hihat_base": 70,
            "hihat_variation": 10,
        },
        "humanization": {
            "timing_jitter": 0.005,
            "velocity_jitter": 0.05,
            "swing_amount": 0.0,
        },
        "fills": {"frequency": 0.2, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "build": {"density_modifier": 0.8, "use_patterns": ["basic", "accent"]},
            "drop": {"density_modifier": 1.0, "use_patterns": ["basic", "accent"]},
            "break": {"density_modifier": 0.3, "use_patterns": ["basic"]},
        },
    },
    "minimal_techno": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
                "click": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 95,
            "click_base": 40,
        },
        "humanization": {
            "timing_jitter": 0.005,
            "velocity_jitter": 0.05,
            "swing_amount": 0.0,
        },
        "fills": {"frequency": 0.1, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.3, "use_patterns": ["basic"]},
            "build": {"density_modifier": 0.6, "use_patterns": ["basic"]},
            "drop": {"density_modifier": 0.8, "use_patterns": ["basic"]},
        },
    },
    "dubstep": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
            },
        },
        "velocities": {
            "kick_base": 110,
            "snare_base": 100,
            "hihat_base": 65,
        },
        "humanization": {
            "timing_jitter": 0.01,
            "velocity_jitter": 0.1,
            "swing_amount": 0.0,
        },
        "fills": {"frequency": 0.3, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "build": {"density_modifier": 0.8, "use_patterns": ["basic"]},
            "drop": {"density_modifier": 1.0, "use_patterns": ["basic"]},
        },
    },
    "dnb": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            },
            "amen_break": {
                "kick":  [1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,1,0,0,1,0,0,1,0,1],
                "hihat": [1,0,1,1,0,1,1,0,1,0,1,1,0,1,1,0],
            },
        },
        "velocities": {
            "kick_base": 110,
            "snare_base": 100,
            "hihat_base": 70,
            "hihat_variation": 20,
        },
        "humanization": {
            "timing_jitter": 0.015,
            "velocity_jitter": 0.12,
            "swing_amount": 0.0,
        },
        "fills": {
            "frequency": 0.4,
            "patterns": [
                {"kick": [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 "snare": [0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,1],
                 "hihat": [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]},
            ],
        },
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.7, "use_patterns": ["basic", "amen_break"]},
            "chorus": {"density_modifier": 1.0, "use_patterns": ["basic", "amen_break"]},
        },
    },

    # ───────── CINEMATIC / ATMOS ─────────
    "ambient": {
        "patterns": {
            "sparse": {
                "kick":  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                "crash": [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
            },
        },
        "velocities": {
            "kick_base": 50,
            "crash_base": 40,
        },
        "humanization": {
            "timing_jitter": 0.05,
            "velocity_jitter": 0.3,
            "swing_amount": 0.0,
        },
        "fills": {"frequency": 0.05, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.3, "use_patterns": ["sparse"]},
            "verse": {"density_modifier": 0.4, "use_patterns": ["sparse"]},
            "chorus": {"density_modifier": 0.6, "use_patterns": ["sparse"]},
        },
    },
    "cinematic": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                "timpani": [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                "crash": [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
            },
        },
        "velocities": {
            "kick_base": 80,
            "timpani_base": 70,
            "crash_base": 60,
        },
        "humanization": {
            "timing_jitter": 0.03,
            "velocity_jitter": 0.2,
            "swing_amount": 0.0,
        },
        "fills": {"frequency": 0.2, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.4, "use_patterns": ["basic"]},
            "build": {"density_modifier": 0.7, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.9, "use_patterns": ["basic"]},
        },
    },
    "downtempo": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 80,
            "snare_base": 75,
            "hihat_base": 55,
        },
        "humanization": {
            "timing_jitter": 0.03,
            "velocity_jitter": 0.2,
            "swing_amount": 0.2,
        },
        "fills": {"frequency": 0.2, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.4, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.7, "use_patterns": ["basic"]},
        },
    },

    # ───────── BAND / ACOUSTIC ─────────
    "rock": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            },
            "fill": {
                "kick":  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,1,0,0,1,0,1],
                "tom_high": [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                "tom_mid": [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
                "tom_low": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            },
        },
        "velocities": {
            "kick_base": 100,
            "snare_base": 100,
            "hihat_base": 75,
            "tom_base": 85,
        },
        "humanization": {
            "timing_jitter": 0.02,
            "velocity_jitter": 0.15,
            "swing_amount": 0.0,
        },
        "fills": {
            "frequency": 0.5,
            "patterns": [
                {"kick": [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 "snare": [0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,1],
                 "tom_high": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 "tom_mid": [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
                 "tom_low": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                 "crash": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]},
            ],
        },
        "section_variations": {
            "intro": {"density_modifier": 0.6, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.7, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.95, "use_patterns": ["basic", "fill"]},
            "bridge": {"density_modifier": 0.8, "use_patterns": ["basic"]},
        },
    },
    "funk": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0],
                "hihat": [1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1],
            },
            "ghost": {
                "kick":  [1,0,0,1,0,1,0,0,1,0,0,1,0,0,0,0],
                "snare": [0,0,40,0,90,0,40,0,0,0,80,0,40,0,0,0],  # Ghost notes encoded
                "hihat": [1,1,0,1,1,0,1,1,0,1,0,1,1,0,0,1],
            },
        },
        "velocities": {
            "kick_base": 95,
            "snare_base": 95,
            "hihat_base": 80,
            "ghost_note_max": 45,
        },
        "humanization": {
            "timing_jitter": 0.03,
            "velocity_jitter": 0.2,
            "swing_amount": 0.3,
        },
        "fills": {
            "frequency": 0.5,
            "patterns": [
                {"kick": [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 "snare": [0,0,0,0,1,0,1,0,0,1,0,0,1,0,0,0],
                 "hihat": [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},
            ],
        },
        "section_variations": {
            "intro": {"density_modifier": 0.6, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.8, "use_patterns": ["basic", "ghost"]},
            "chorus": {"density_modifier": 1.0, "use_patterns": ["basic", "ghost"]},
        },
    },
    "jazz": {
        "patterns": {
            "ride": {
                "kick":  [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],  # Feather bass drum
                "hihat": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],  # Foot on 2 & 4
                "ride":  [1,0,1,0,1,1,1,0,1,0,1,0,1,1,1,0],  # Swing pattern
            },
            "comp": {
                "kick":  [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],  # Comping kicks
                "snare": [0,0,30,0,0,0,35,0,0,0,30,0,0,0,40,0],  # Comping snare
                "hihat": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
                "ride":  [1,0,1,0,1,1,1,0,1,0,1,0,1,1,1,0],
            },
        },
        "velocities": {
            "kick_base": 55,  # Feather bass drum
            "snare_base": 35,  # Ghost comping
            "hihat_base": 85,
            "ride_base": 75,
        },
        "humanization": {
            "timing_jitter": 0.04,
            "velocity_jitter": 0.25,
            "swing_amount": 0.45,
        },
        "fills": {"frequency": 0.3, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["ride"]},
            "verse": {"density_modifier": 0.6, "use_patterns": ["ride", "comp"]},
            "chorus": {"density_modifier": 0.8, "use_patterns": ["ride", "comp"]},
            "solo": {"density_modifier": 0.9, "use_patterns": ["ride", "comp"]},
        },
    },

    # ───────── SYNTH / RETRO / ELECTRONIC ─────────
    "synthpop": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 100,
            "snare_base": 90,
            "hihat_base": 70,
        },
        "humanization": {
            "timing_jitter": 0.01,
            "velocity_jitter": 0.08,
            "swing_amount": 0.05,
        },
        "fills": {"frequency": 0.3, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.7, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.95, "use_patterns": ["basic"]},
        },
    },
    "synthwave": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
                "tom":   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            },
            "gated": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,1,0,0,0,0,1,0,0,1],  # Gated reverb feel
                "hihat": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 100,
            "snare_base": 95,
            "hihat_base": 65,
            "tom_base": 80,
        },
        "humanization": {
            "timing_jitter": 0.01,
            "velocity_jitter": 0.1,
            "swing_amount": 0.0,
        },
        "fills": {
            "frequency": 0.4,
            "patterns": [
                {"kick": [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 "snare": [0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                 "tom": [0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,1]},
            ],
        },
        "section_variations": {
            "intro": {"density_modifier": 0.4, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.6, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.9, "use_patterns": ["basic", "gated"]},
        },
    },
    "retrowave": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 100,
            "snare_base": 90,
            "hihat_base": 65,
        },
        "humanization": {
            "timing_jitter": 0.01,
            "velocity_jitter": 0.1,
            "swing_amount": 0.0,
        },
        "fills": {"frequency": 0.3, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.7, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.95, "use_patterns": ["basic"]},
        },
    },
    "outrun": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,1,0,1,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 105,
            "snare_base": 95,
            "hihat_base": 70,
        },
        "humanization": {
            "timing_jitter": 0.01,
            "velocity_jitter": 0.1,
            "swing_amount": 0.0,
        },
        "fills": {"frequency": 0.35, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.7, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.95, "use_patterns": ["basic"]},
        },
    },
    "darkwave": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 95,
            "snare_base": 85,
            "hihat_base": 60,
        },
        "humanization": {
            "timing_jitter": 0.01,
            "velocity_jitter": 0.1,
            "swing_amount": 0.0,
        },
        "fills": {"frequency": 0.25, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.4, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.6, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.85, "use_patterns": ["basic"]},
        },
    },
    "ebm": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
                "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 110,
            "snare_base": 95,
            "hihat_base": 70,
        },
        "humanization": {
            "timing_jitter": 0.01,
            "velocity_jitter": 0.08,
            "swing_amount": 0.0,
        },
        "fills": {"frequency": 0.2, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.7, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.95, "use_patterns": ["basic"]},
        },
    },
    "electro": {
        "patterns": {
            "basic": {
                "kick":  [1,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1],
            },
        },
        "velocities": {
            "kick_base": 95,
            "snare_base": 90,
            "hihat_base": 75,
        },
        "humanization": {
            "timing_jitter": 0.02,
            "velocity_jitter": 0.15,
            "swing_amount": 0.1,
        },
        "fills": {"frequency": 0.35, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.7, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.95, "use_patterns": ["basic"]},
        },
    },
    "idm": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0],
                "snare": [0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,1],
                "hihat": [1,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0],
            },
            "glitch": {
                "kick":  [1,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0],
                "snare": [0,0,1,0,0,0,0,1,0,0,1,0,0,0,0,0],
                "hihat": [1,0,0,1,0,1,0,0,0,1,0,0,1,0,1,0],
                "click": [0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0],
            },
        },
        "velocities": {
            "kick_base": 90,
            "snare_base": 85,
            "hihat_base": 65,
            "click_base": 40,
        },
        "humanization": {
            "timing_jitter": 0.03,
            "velocity_jitter": 0.2,
            "swing_amount": 0.2,
        },
        "fills": {"frequency": 0.4, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.7, "use_patterns": ["basic", "glitch"]},
            "chorus": {"density_modifier": 0.9, "use_patterns": ["basic", "glitch"]},
        },
    },
    "glitch": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0],
                "snare": [0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0],
                "hihat": [1,0,0,1,0,1,0,0,1,0,0,1,0,1,0,0],
                "click": [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
            },
        },
        "velocities": {
            "kick_base": 85,
            "snare_base": 80,
            "hihat_base": 55,
            "click_base": 35,
        },
        "humanization": {
            "timing_jitter": 0.04,
            "velocity_jitter": 0.25,
            "swing_amount": 0.25,
        },
        "fills": {"frequency": 0.3, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.4, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 0.7, "use_patterns": ["basic"]},
        },
    },
    "electronic_pop": {
        "patterns": {
            "basic": {
                "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
            },
        },
        "velocities": {
            "kick_base": 105,
            "snare_base": 95,
            "hihat_base": 70,
        },
        "humanization": {
            "timing_jitter": 0.01,
            "velocity_jitter": 0.08,
            "swing_amount": 0.05,
        },
        "fills": {"frequency": 0.35, "patterns": []},
        "section_variations": {
            "intro": {"density_modifier": 0.5, "use_patterns": ["basic"]},
            "verse": {"density_modifier": 0.7, "use_patterns": ["basic"]},
            "pre_chorus": {"density_modifier": 0.85, "use_patterns": ["basic"]},
            "chorus": {"density_modifier": 1.0, "use_patterns": ["basic"]},
        },
    },
}

# Default configs for unknown styles
DEFAULT_DRUM_CONFIG = {
    "patterns": {
        "basic": {
            "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
            "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
            "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
        },
    },
    "velocities": {
        "kick_base": 90,
        "snare_base": 90,
        "hihat_base": 70,
        "hihat_variation": 20,
        "ghost_note_max": 40,
    },
    "humanization": {
        "timing_jitter": 0.02,
        "velocity_jitter": 0.15,
        "swing_amount": 0.1,
    },
    "fills": {"frequency": 0.3, "patterns": []},
    "section_variations": {
        "default": {"density_modifier": 0.7, "use_patterns": ["basic"]},
    },
}

DEFAULT_BASS_CONFIG = {
    "approach": "simple",
    "scale_preference": ["root", "fifth", "octave"],
    "rhythmic_density": 0.5,
    "octave_range": (1, 2),
    "note_lengths": ["quarter", "half"],
    "syncopation": 0.3,
    "approach_patterns": ["direct"],
    "slide_frequency": 0.1,
    "variation_on_repeat": False,
}

# ============================================================================
# STYLE LIBRARY
# ============================================================================
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
            "lead": ["Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 5 (charang)"],
            "pad": ["Pad 1 (new age)", "Pad 2 (warm)", "Pad 5 (bowed)"],
            "bass": ["Electric Bass (finger)", "Synth Bass 1", "Fretless Bass"]
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
            "lead": ["Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 6 (voice)"],
            "pad": ["Pad 5 (bowed)", "Pad 4 (choir)", "Pad 2 (warm)"],
            "bass": ["Electric Bass (finger)", "Synth Bass 2", "Fretless Bass"]
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
            "lead": ["Electric Piano 1", "Electric Piano 2", "Acoustic Grand Piano"],
            "pad": ["String Ensemble 1", "Pad 2 (warm)", "Synth Strings 1"],
            "bass": ["Electric Bass (finger)", "Electric Bass (pick)", "Acoustic Bass"]
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
            "lead": ["Electric Piano 1", "Electric Piano 2", "Pad 1 (new age)"],
            "pad": ["Pad 1 (new age)", "Pad 2 (warm)", "Pad 5 (bowed)"],
            "bass": ["Electric Bass (finger)", "Fretless Bass", "Synth Bass 1"]
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
            "lead": ["Synth Brass 1", "Lead 1 (square)", "Lead 2 (sawtooth)"],
            "pad": ["Pad 1 (new age)", "Pad 3 (polysynth)", "Synth Strings 1"],
            "bass": ["Synth Bass 1", "Synth Bass 2", "Electric Bass (finger)"]
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
            "lead": ["Synth Strings 1", "Lead 6 (voice)", "Electric Piano 1"],
            "pad": ["Pad 2 (warm)", "Pad 1 (new age)", "Pad 5 (bowed)"],
            "bass": ["Synth Bass 1", "Electric Bass (finger)", "Fretless Bass"]
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
            "lead": ["Lead 6 (voice)", "Lead 2 (sawtooth)", "Synth Brass 1"],
            "pad": ["Pad 4 (choir)", "Pad 5 (bowed)", "Pad 8 (sweep)"],
            "bass": ["Synth Bass 1", "Synth Bass 2", "Fretless Bass"]
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
            "lead": ["Lead 1 (square)", "Lead 4 (chiff)", "Lead 8 (bass + lead)"],
            "pad": ["Pad 8 (sweep)", "Pad 6 (metallic)", "Pad 7 (halo)"],
            "bass": ["Synth Bass 1", "Synth Bass 2", "Lead 8 (bass + lead)"]
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
            "lead": ["Lead 1 (square)", "Lead 2 (sawtooth)", "Synth Brass 2"],
            "pad": ["Pad 5 (bowed)", "Pad 4 (choir)", "Pad 6 (metallic)"],
            "bass": ["Synth Bass 2", "Synth Bass 1", "Fretless Bass"]
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
            "lead": ["Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 5 (charang)"],
            "pad": ["Pad 1 (new age)", "Pad 3 (polysynth)", "Synth Strings 1"],
            "bass": ["Synth Bass 1", "Synth Bass 2", "Electric Bass (finger)"]
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
            "lead": ["Pad 1 (new age)", "Pad 2 (warm)", "Pad 5 (bowed)"],
            "pad": ["Pad 4 (choir)", "Pad 5 (bowed)", "Pad 7 (halo)"],
            "bass": ["Pad 5 (bowed)", "Synth Bass 2", "Acoustic Bass"]
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
            "lead": ["String Ensemble 1", "Orchestra Hit", "French Horn"],
            "pad": ["Pad 4 (choir)", "Pad 5 (bowed)", "String Ensemble 1"],
            "bass": ["Pad 5 (bowed)", "Timpani", "Contrabass"]
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
            "lead": ["Electric Piano 1", "Electric Piano 2", "Lead 6 (voice)"],
            "pad": ["Pad 2 (warm)", "Pad 1 (new age)", "Synth Strings 1"],
            "bass": ["Electric Bass (finger)", "Fretless Bass", "Synth Bass 1"]
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
            "lead": ["Electric Guitar (clean)", "Overdriven Guitar", "Electric Piano 1"],
            "pad": ["String Ensemble 1", "Pad 2 (warm)", "Synth Strings 1"],
            "bass": ["Electric Bass (finger)", "Electric Bass (pick)", "Slap Bass 1"]
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
            "lead": ["Electric Guitar (clean)", "Electric Piano 1", "Alto Sax"],
            "pad": ["Electric Piano 1", "Pad 2 (warm)", "String Ensemble 1"],
            "bass": ["Electric Bass (finger)", "Slap Bass 1", "Fretless Bass"]
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
            "lead": ["Acoustic Grand Piano", "Electric Piano 1", "Tenor Sax"],
            "pad": ["String Ensemble 1", "Pad 2 (warm)", "Electric Piano 1"],
            "bass": ["Acoustic Bass", "Electric Bass (finger)", "Fretless Bass"]
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
            "lead": ["Lead 1 (square)", "Lead 2 (sawtooth)", "Synth Brass 1"],
            "pad": ["Pad 1 (new age)", "Pad 3 (polysynth)", "Synth Strings 1"],
            "bass": ["Synth Bass 1", "Synth Bass 2", "Electric Bass (finger)"]
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
            "lead": ["Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 5 (charang)"],
            "pad": ["Pad 1 (new age)", "Pad 2 (warm)", "Pad 5 (bowed)"],
            "bass": ["Synth Bass 2", "Synth Bass 1", "Fretless Bass"]
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
            "lead": ["Lead 1 (square)", "Lead 2 (sawtooth)", "Synth Brass 1"],
            "pad": ["Pad 1 (new age)", "Pad 3 (polysynth)", "Pad 5 (bowed)"],
            "bass": ["Synth Bass 1", "Synth Bass 2", "Electric Bass (finger)"]
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
            "lead": ["Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 5 (charang)"],
            "pad": ["Pad 1 (new age)", "Pad 5 (bowed)", "Pad 6 (metallic)"],
            "bass": ["Synth Bass 2", "Synth Bass 1", "Fretless Bass"]
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
            "lead": ["Lead 6 (voice)", "Lead 2 (sawtooth)", "Pad 5 (bowed)"],
            "pad": ["Pad 4 (choir)", "Pad 5 (bowed)", "Pad 6 (metallic)"],
            "bass": ["Synth Bass 2", "Synth Bass 1", "Fretless Bass"]
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
            "lead": ["Lead 1 (square)", "Lead 2 (sawtooth)", "Synth Brass 1"],
            "pad": ["Pad 5 (bowed)", "Pad 4 (choir)", "Pad 6 (metallic)"],
            "bass": ["Synth Bass 1", "Synth Bass 2", "Fretless Bass"]
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
            "lead": ["Electric Piano 1", "Electric Piano 2", "Alto Sax"],
            "pad": ["Pad 1 (new age)", "Pad 2 (warm)", "String Ensemble 1"],
            "bass": ["Electric Bass (finger)", "Fretless Bass", "Slap Bass 1"]
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
            "lead": ["Lead 1 (square)", "Lead 4 (chiff)", "Lead 8 (bass + lead)"],
            "pad": ["Pad 8 (sweep)", "Pad 6 (metallic)", "Pad 7 (halo)"],
            "bass": ["Synth Bass 2", "Synth Bass 1", "Lead 8 (bass + lead)"]
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
            "lead": ["Lead 1 (square)", "Lead 4 (chiff)", "FX 8 (sci-fi)"],
            "pad": ["Pad 8 (sweep)", "Pad 6 (metallic)", "FX 4 (atmosphere)"],
            "bass": ["Synth Bass 2", "Synth Bass 1", "Lead 8 (bass + lead)"]
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
            "lead": ["Lead 1 (square)", "Lead 2 (sawtooth)", "Synth Brass 1"],
            "pad": ["Pad 1 (new age)", "Pad 3 (polysynth)", "Synth Strings 1"],
            "bass": ["Synth Bass 1", "Synth Bass 2", "Electric Bass (finger)"]
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