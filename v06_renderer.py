"""
Offline v0.6 song renderer.

This module creates deterministic MIDI and WAV previews from the v0.6 project
document. It is intentionally small and dependency-light: the goal is to test
project structure, instrument routing and asset export without requiring
MusicGen or external MIDI libraries.
"""

from __future__ import annotations

import math
import os
import struct
import wave
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np

from daw_engine import DAWPart, DAWProject, NOTE_NAMES, SCALE_PATTERNS


TICKS_PER_BEAT = 480
FLATS = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
NOTE_TO_PC = {name: i for i, name in enumerate(NOTE_NAMES)}
DRUM_NOTES = {"kick": 36, "snare": 38, "hat": 42, "clap": 39}


@dataclass
class NoteEvent:
    track_id: str
    channel: int
    note: int
    velocity: int
    start_beat: float
    duration_beats: float
    instrument: str


class OfflineSongRenderer:
    """Render a DAWProject to a project JSON, MIDI file and WAV preview."""

    def __init__(self, sample_rate: int = 32000):
        self.sample_rate = sample_rate

    def render_project(self, project: DAWProject, output_dir: str) -> Dict[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        events = self.build_events(project)

        midi_master_path = os.path.join(output_dir, "song.mid")
        midi_track_paths = self._track_midi_paths(project, output_dir)
        wav_path = os.path.join(output_dir, "song.wav")
        project_path = os.path.join(output_dir, "project.json")

        self.write_midi(project, events, midi_master_path)
        self.write_track_midis(project, events, midi_track_paths)
        self.write_wav(project, events, wav_path)
        project.render_settings["master_audio_path"] = wav_path

        for part in project.parts:
            part.analysis["midi_master_path"] = midi_master_path
            if part.track_id in midi_track_paths:
                part.analysis["midi_track_path"] = midi_track_paths[part.track_id]
            part.analysis["offline_renderer"] = "v0.6"
            if not part.duration:
                part.duration = part.duration_seconds
            project.record_generation(
                part=part,
                prompt=part.build_prompt(),
                audio_path=wav_path,
                analysis=part.analysis,
                warnings=["offline_preview_renderer"],
            )

        project.save(project_path)
        paths = {"json": project_path, "midi": midi_master_path, "wav": wav_path}
        for track_id, track_path in midi_track_paths.items():
            paths[f"midi_{track_id}"] = track_path
        return paths

    def build_events(self, project: DAWProject) -> List[NoteEvent]:
        events: List[NoteEvent] = []
        for part in project.parts:
            if part.instrument_class in ("drums", "percussion"):
                events.extend(self._drum_events(project, part))
            elif part.instrument_class == "bass":
                events.extend(self._bass_events(project, part))
            elif part.instrument_class in ("chords", "pad", "arpeggio"):
                events.extend(self._chord_events(project, part))
            elif part.instrument_class in ("lead", "melody", "vocals"):
                events.extend(self._lead_events(project, part))
            elif part.instrument_class == "fx":
                events.extend(self._fx_events(project, part))
        return sorted(events, key=lambda e: (e.start_beat, e.channel, e.note))

    def _drum_events(self, project: DAWProject, part: DAWPart) -> Iterable[NoteEvent]:
        groove = project.groove.lower()
        beats = project.beats_per_bar()
        start = self._part_start_beat(project, part)
        patterns = {
            "rock": {
                "kick": [0.0, 2.0],
                "snare": [1.0, 3.0],
                "hat": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
            },
            "lofi": {
                "kick": [0.0, 2.5],
                "snare": [2.0],
                "hat": [0.0, 1.0, 2.0, 3.0],
            },
            "trap": {
                "kick": [0.0, 1.5, 3.0],
                "snare": [2.0],
                "hat": [0.0, 0.5, 1.0, 1.5, 2.0, 2.25, 2.5, 2.75, 3.0, 3.5],
            },
            "synthwave": {
                "kick": [0.0, 2.0],
                "snare": [1.0, 3.0],
                "hat": [0.5, 1.5, 2.5, 3.5],
            },
        }
        pattern = patterns.get(groove, patterns["trap"])
        for bar in range(part.measures):
            bar_start = start + bar * beats
            for drum, offsets in pattern.items():
                for offset in offsets:
                    yield NoteEvent(
                        part.track_id, 9, DRUM_NOTES[drum], 105 if drum != "hat" else 72,
                        bar_start + offset, 0.12, drum,
                    )

    def _bass_events(self, project: DAWProject, part: DAWPart) -> Iterable[NoteEvent]:
        beats = project.beats_per_bar()
        start = self._part_start_beat(project, part)
        for bar in range(part.measures):
            root, _, fifth = self._chord_notes(project, bar, octave=2)
            bar_start = start + bar * beats
            if project.groove.lower() == "synthwave":
                sequence = [(root, i * 0.5, 0.42) for i in range(4)]
                sequence += [(fifth, 2.0 + i * 0.5, 0.42) for i in range(4)]
            else:
                sequence = [(root, 0.0, 0.9), (root, 1.5, 0.45), (fifth, 2.5, 0.7), (root, 3.5, 0.4)]
            for note, offset, duration in sequence:
                yield NoteEvent(part.track_id, 2, note, 92, bar_start + offset, duration, part.instrument)

    def _chord_events(self, project: DAWProject, part: DAWPart) -> Iterable[NoteEvent]:
        beats = project.beats_per_bar()
        start = self._part_start_beat(project, part)
        for bar in range(part.measures):
            notes = self._chord_notes(project, bar, octave=4)
            for note in notes:
                yield NoteEvent(part.track_id, 1, note, 72, start + bar * beats, beats * 0.92, part.instrument)

    def _lead_events(self, project: DAWProject, part: DAWPart) -> Iterable[NoteEvent]:
        beats = project.beats_per_bar()
        start = self._part_start_beat(project, part)
        scale = SCALE_PATTERNS.get(project.scale, SCALE_PATTERNS["natural_minor"])
        root_pc = NOTE_TO_PC.get(project.root, 0)
        motif = [0, 2, 4, 5, 4, 2, 1, 0]
        step = 0.5
        for bar in range(part.measures):
            for i, degree in enumerate(motif):
                pc = (root_pc + scale[degree % len(scale)]) % 12
                note = 72 + pc
                yield NoteEvent(part.track_id, 3, note, 78, start + bar * beats + i * step, step * 0.82, part.instrument)

    def _fx_events(self, project: DAWProject, part: DAWPart) -> Iterable[NoteEvent]:
        start = self._part_start_beat(project, part)
        yield NoteEvent(part.track_id, 4, 84, 55, start, part.total_beats, part.instrument)

    def write_midi(self, project: DAWProject, events: List[NoteEvent], filepath: str):
        tracks: List[bytes] = [self._tempo_track(project)]
        by_track: Dict[str, List[NoteEvent]] = {}
        for event in events:
            by_track.setdefault(event.track_id, []).append(event)

        for track in project.tracks:
            track_events = by_track.get(track.id, [])
            tracks.append(self._note_track(track.name, track_events))

        header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), TICKS_PER_BEAT)
        with open(filepath, "wb") as f:
            f.write(header)
            for track_data in tracks:
                f.write(b"MTrk" + struct.pack(">I", len(track_data)) + track_data)

    def write_track_midis(self, project: DAWProject, events: List[NoteEvent],
                          track_paths: Dict[str, str]):
        by_track: Dict[str, List[NoteEvent]] = {}
        for event in events:
            by_track.setdefault(event.track_id, []).append(event)

        for track in project.tracks:
            track_events = by_track.get(track.id, [])
            if not track_events:
                continue
            track_project = DAWProject(
                name=f"{project.name} - {track.name}",
                bpm=project.bpm,
                division=project.division,
                root=project.root,
                scale=project.scale,
                chord_progression=project.chord_progression,
                groove=project.groove,
                swing=project.swing,
            )
            track_project.tracks = [track]
            self.write_midi(track_project, track_events, track_paths[track.id])

    def write_wav(self, project: DAWProject, events: List[NoteEvent], filepath: str):
        duration = max(project.total_duration, 1.0) + 0.25
        audio = np.zeros((int(duration * self.sample_rate), 2), dtype=np.float32)

        for event in events:
            start = int(event.start_beat * 60.0 / project.bpm * self.sample_rate)
            length = max(1, int(event.duration_beats * 60.0 / project.bpm * self.sample_rate))
            end = min(audio.shape[0], start + length)
            if start >= end:
                continue
            segment = self._synthesize_event(event, end - start)
            pan = self._track_pan(project, event.track_id)
            left = 1.0 - max(0.0, pan)
            right = 1.0 - max(0.0, -pan)
            audio[start:end, 0] += segment * left
            audio[start:end, 1] += segment * right

        peak = float(np.max(np.abs(audio))) if audio.size else 0.0
        if peak > 0:
            audio = audio / max(peak, 1.0) * 0.88
        audio = np.clip(audio, -1.0, 1.0)
        pcm = (audio * 32767).astype("<i2")

        with wave.open(filepath, "wb") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            wav.writeframes(pcm.tobytes())

    def _tempo_track(self, project: DAWProject) -> bytes:
        events = bytearray()
        tempo = int(60_000_000 / project.bpm)
        numerator, denominator = self._time_signature(project.division)
        events += self._var_len(0) + bytes([0xFF, 0x51, 0x03]) + tempo.to_bytes(3, "big")
        events += self._var_len(0) + bytes([0xFF, 0x58, 0x04, numerator, int(math.log2(denominator)), 24, 8])
        events += self._track_name("Tempo")
        events += self._end_track()
        return bytes(events)

    def _note_track(self, name: str, events: List[NoteEvent]) -> bytes:
        output = bytearray()
        output += self._track_name(name)
        timeline: List[Tuple[int, bytes]] = []
        program_by_channel = {1: 88, 2: 38, 3: 81, 4: 95}
        for channel, program in program_by_channel.items():
            timeline.append((0, bytes([0xC0 | channel, program])))
        for event in events:
            start = int(event.start_beat * TICKS_PER_BEAT)
            end = int((event.start_beat + event.duration_beats) * TICKS_PER_BEAT)
            timeline.append((start, bytes([0x90 | event.channel, event.note, event.velocity])))
            timeline.append((end, bytes([0x80 | event.channel, event.note, 0])))

        last_tick = 0
        for tick, data in sorted(timeline, key=lambda item: (item[0], item[1][0] & 0xF0)):
            output += self._var_len(max(0, tick - last_tick)) + data
            last_tick = tick
        output += self._end_track()
        return bytes(output)

    def _synthesize_event(self, event: NoteEvent, samples: int) -> np.ndarray:
        t = np.arange(samples, dtype=np.float32) / self.sample_rate
        amp = event.velocity / 127.0
        env = np.exp(-t * 8.0)
        if event.channel == 9:
            if event.note == DRUM_NOTES["kick"]:
                freq = 65.0 * np.exp(-t * 18.0) + 38.0
                wave_data = np.sin(2 * np.pi * freq * t) * np.exp(-t * 9.0)
            elif event.note == DRUM_NOTES["snare"]:
                noise = self._noise(samples, event.note)
                tone = np.sin(2 * np.pi * 190.0 * t)
                wave_data = (noise * 0.65 + tone * 0.35) * np.exp(-t * 12.0)
            else:
                wave_data = self._noise(samples, event.note) * np.exp(-t * 30.0)
            return (wave_data * amp * 0.8).astype(np.float32)

        freq = 440.0 * (2 ** ((event.note - 69) / 12.0))
        if event.channel == 2:
            wave_data = np.sign(np.sin(2 * np.pi * freq * t)) * 0.55
        elif event.channel == 1:
            wave_data = np.sin(2 * np.pi * freq * t) * 0.55 + np.sin(2 * np.pi * freq * 2 * t) * 0.12
        else:
            wave_data = np.sin(2 * np.pi * freq * t)
        return (wave_data * env * amp * 0.28).astype(np.float32)

    def _chord_notes(self, project: DAWProject, bar_index: int, octave: int) -> Tuple[int, int, int]:
        chord = project.chord_progression[bar_index % len(project.chord_progression)] if project.chord_progression else project.root
        root_name, is_minor = self._parse_chord(chord)
        root_pc = NOTE_TO_PC.get(root_name, NOTE_TO_PC.get(project.root, 0))
        base = 12 * (octave + 1) + root_pc
        third = base + (3 if is_minor else 4)
        fifth = base + 7
        return base, third, fifth

    def _parse_chord(self, chord: str) -> Tuple[str, bool]:
        cleaned = chord.strip()
        if len(cleaned) >= 2 and cleaned[1] in ("#", "b"):
            root = cleaned[:2]
            suffix = cleaned[2:]
        else:
            root = cleaned[:1]
            suffix = cleaned[1:]
        root = FLATS.get(root, root)
        return root, suffix.startswith("m") and not suffix.startswith("maj")

    def _part_start_beat(self, project: DAWProject, part: DAWPart) -> float:
        return max(0.0, (part.start_bar - 1.0) * project.beats_per_bar())

    def _track_pan(self, project: DAWProject, track_id: str) -> float:
        track = project.find_track(track_id)
        return track.pan if track else 0.0

    def _track_midi_paths(self, project: DAWProject, output_dir: str) -> Dict[str, str]:
        midi_dir = os.path.join(output_dir, "midi_tracks")
        os.makedirs(midi_dir, exist_ok=True)
        return {
            track.id: os.path.join(midi_dir, f"{track.id}.mid")
            for track in project.tracks
        }

    def _time_signature(self, division: str) -> Tuple[int, int]:
        try:
            numerator, denominator = division.split("/")
            return int(numerator), int(denominator)
        except ValueError:
            return 4, 4

    def _noise(self, samples: int, seed: int) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return rng.uniform(-1.0, 1.0, samples).astype(np.float32)

    def _track_name(self, name: str) -> bytes:
        encoded = name.encode("utf-8")
        return self._var_len(0) + bytes([0xFF, 0x03, len(encoded)]) + encoded

    def _end_track(self) -> bytes:
        return self._var_len(0) + bytes([0xFF, 0x2F, 0x00])

    def _var_len(self, value: int) -> bytes:
        buffer = value & 0x7F
        value >>= 7
        bytes_out = [buffer]
        while value:
            buffer = (value & 0x7F) | 0x80
            bytes_out.insert(0, buffer)
            value >>= 7
        return bytes(bytes_out)
