"""
Parametric song factory for Studio Onyrix v0.6.

The factory turns a genre/style name into a full DAWProject: global musical
settings, arrangement sections, tracks and generated parts. It is the bridge
between a future DAW UI and the lower-level engine dataclasses.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from daw_engine import DAWPart, DAWProject


STYLE_PRESETS: Dict[str, Dict[str, Any]] = {
    "trap": {
        "bpm": 140,
        "root": "A",
        "scale": "natural_minor",
        "chords": ["Am", "F", "C", "G"],
        "groove": "trap",
        "swing": 0.10,
        "style_tags": ["trap", "dark", "808"],
        "instruments": {
            "drums": "trap_drums",
            "bass": "808_bass",
            "chords": "synth_pad",
            "lead": "synth_lead",
            "fx": "riser",
        },
    },
    "synthwave": {
        "bpm": 100,
        "root": "D",
        "scale": "natural_minor",
        "chords": ["Dm", "Bb", "F", "C"],
        "groove": "synthwave",
        "swing": 0.0,
        "style_tags": ["synthwave", "retro", "cinematic"],
        "instruments": {
            "drums": "drums_full",
            "bass": "synth_bass",
            "chords": "synth_pad",
            "lead": "synth_lead",
            "fx": "noise_sweep",
        },
    },
    "lofi": {
        "bpm": 78,
        "root": "C",
        "scale": "major",
        "chords": ["Cmaj7", "Am", "Fmaj7", "G"],
        "groove": "lofi",
        "swing": 0.18,
        "style_tags": ["lofi", "warm", "chill"],
        "instruments": {
            "drums": "drums_full",
            "bass": "pluck_bass",
            "chords": "wurlitzer",
            "lead": "flute",
            "fx": "texture_pad",
        },
    },
    "rock": {
        "bpm": 126,
        "root": "E",
        "scale": "minor_pentatonic",
        "chords": ["Em", "G", "D", "A"],
        "groove": "rock",
        "swing": 0.0,
        "style_tags": ["rock", "garage", "live"],
        "instruments": {
            "drums": "drums_full",
            "bass": "pluck_bass",
            "chords": "piano",
            "lead": "guitar_melody",
            "fx": "noise_sweep",
        },
    },
}


DEFAULT_ARRANGEMENT: List[Dict[str, Any]] = [
    {"type": "intro", "start_bar": 1, "bars": 4, "energy": 0.35, "tracks": ["chords", "fx"]},
    {"type": "verse", "start_bar": 5, "bars": 8, "energy": 0.65, "tracks": ["drums", "bass", "chords"]},
    {"type": "chorus", "start_bar": 13, "bars": 8, "energy": 0.90, "tracks": ["drums", "bass", "chords", "lead"]},
    {"type": "outro", "start_bar": 21, "bars": 4, "energy": 0.45, "tracks": ["chords", "lead", "fx"]},
]


TRACK_CLASSES = {
    "drums": "drums",
    "bass": "bass",
    "chords": "chords",
    "lead": "lead",
    "fx": "fx",
}


def available_styles() -> List[str]:
    return sorted(STYLE_PRESETS)


def create_song_project(
    style: str,
    name: Optional[str] = None,
    bpm: Optional[int] = None,
    root: Optional[str] = None,
    scale: Optional[str] = None,
    chords: Optional[List[str]] = None,
    arrangement: Optional[List[Dict[str, Any]]] = None,
    measures: Optional[int] = None,
) -> DAWProject:
    """Create a full multi-track project from style parameters."""
    if style not in STYLE_PRESETS:
        raise ValueError(f"Unknown style '{style}'. Available: {', '.join(available_styles())}")

    preset = deepcopy(STYLE_PRESETS[style])
    project = DAWProject(
        name=name or f"{style.title()} Song",
        bpm=bpm or preset["bpm"],
        root=root or preset["root"],
        scale=scale or preset["scale"],
        chord_progression=chords or preset["chords"],
        groove=preset["groove"],
        swing=preset["swing"],
        style_tags=preset["style_tags"],
        description=f"Parametric Studio Onyrix v0.6 {style} project",
    )
    project.memory["intent"] = (
        f"Generate a complete {style} track as a DAW project with separated "
        "drums, bass, chords, lead and FX tracks."
    )
    project.memory["arrangement"] = []

    sections = deepcopy(arrangement or DEFAULT_ARRANGEMENT)
    if measures:
        sections = _fit_arrangement_to_measures(sections, measures)

    for section in sections:
        project.memory["arrangement"].append(section)
        for track_id in section["tracks"]:
            _add_section_part(project, preset, section, track_id)

    return project


def _add_section_part(project: DAWProject, preset: Dict[str, Any],
                      section: Dict[str, Any], track_id: str):
    instrument = preset["instruments"][track_id]
    instrument_class = TRACK_CLASSES[track_id]
    energy = section.get("energy", 0.6)
    volume = {
        "drums": 0.92,
        "bass": 0.84,
        "chords": 0.68,
        "lead": 0.76,
        "fx": 0.45,
    }.get(track_id, 0.75)
    temperature = 0.55 + energy * 0.55

    part = DAWPart(
        id=f"{project.name.lower().replace(' ', '_')}_{section['type']}_{track_id}",
        bpm=project.bpm,
        division=project.division,
        root=project.root,
        scale=project.scale,
        measures=int(section["bars"]),
        instrument=instrument,
        instrument_class=instrument_class,
        relation=section["type"],
        track_id=track_id,
        start_bar=float(section["start_bar"]),
        volume=volume,
        pan=_default_pan(track_id),
        temperature=temperature,
        extra_prompt=(
            f"{project.groove} {track_id}, section energy {energy:.2f}, "
            f"follow {' - '.join(project.chord_progression)}"
        ),
    )
    project.add_part(part)


def _default_pan(track_id: str) -> float:
    return {
        "drums": 0.0,
        "bass": -0.06,
        "chords": 0.12,
        "lead": 0.20,
        "fx": -0.18,
    }.get(track_id, 0.0)


def _fit_arrangement_to_measures(sections: List[Dict[str, Any]], total_measures: int) -> List[Dict[str, Any]]:
    """Scale section lengths while preserving starts and order."""
    total = sum(int(section["bars"]) for section in sections)
    if total <= 0 or total == total_measures:
        return sections

    scaled = []
    consumed = 0
    current_start = 1
    for index, section in enumerate(sections):
        section = dict(section)
        if index == len(sections) - 1:
            bars = max(1, total_measures - consumed)
        else:
            bars = max(1, round(int(section["bars"]) * total_measures / total))
        section["bars"] = bars
        section["start_bar"] = current_start
        current_start += bars
        consumed += bars
        scaled.append(section)
    return scaled
