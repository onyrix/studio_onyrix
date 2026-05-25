import hashlib
import os
import random

from miditoolkit import Instrument, MidiFile, Note, TempoChange, TimeSignature

from generation.music_config import (
    BAR_TICKS,
    BEATS_PER_BAR,
    CHORD_QUALITIES,
    DRUM_NOTES,
    INSTRUMENT_LIBRARY,
    ROOTS,
    SECTION_LIBRARY,
    STEP_TICKS,
    TICKS_PER_BEAT,
)
from generation.song_config import SongConfig


def parse_chord(name):
    name = name.strip()
    if len(name) > 1 and name[1] in ("#", "b"):
        root_name = name[:2]
        quality = name[2:]
    else:
        root_name = name[:1]
        quality = name[1:]

    if root_name not in ROOTS:
        root_name = "C"

    if quality not in CHORD_QUALITIES:
        quality = "m" if "m" in quality and "maj" not in quality else ""

    return ROOTS[root_name], CHORD_QUALITIES[quality]


def chord_notes(chord_name, octave=4):
    root, intervals = parse_chord(chord_name)
    base = 12 * (octave + 1) + root
    return [base + interval for interval in intervals]


def clamp(value, low, high):
    return max(low, min(high, value))


class SongComposer:
    def __init__(self, config):
        self.config = config
        seed_text = f"{config.title}|{config.style}|{config.mood}|{config.prompt}|{','.join(config.chords)}"
        seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:12], 16)
        self.rng = random.Random(seed)
        self.style = config.style_config()
        self.mood = config.mood_config()
        self.chords = config.resolved_chords()
        self.density = clamp(
            self.style["density"] + self.mood["density"] + self._prompt_density(),
            0.15,
            0.95,
        )
        self.swing = self.style["swing"]
        self.humanize = self._prompt_humanize()

    def compose(self):
        midi = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
        midi.tempo_changes = [TempoChange(self.config.resolved_bpm(), 0)]
        midi.time_signature_changes = [TimeSignature(4, 4, 0)]

        for track_name in self.config.resolved_tracks():
            instrument = self._make_instrument(track_name)
            self._fill_track(instrument, track_name)
            midi.instruments.append(instrument)

        out_dir = os.path.dirname(self.config.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        midi.dump(self.config.output)
        return self.config.output

    def _make_instrument(self, track_name):
        instrument = INSTRUMENT_LIBRARY.get(track_name, INSTRUMENT_LIBRARY["piano"])
        return Instrument(
            program=instrument["program"],
            is_drum=instrument["is_drum"],
            name=track_name,
        )

    def _fill_track(self, instrument, track_name):
        config = INSTRUMENT_LIBRARY.get(track_name, INSTRUMENT_LIBRARY["piano"])
        role = config["role"]

        if role == "drums":
            self._write_drums(instrument)
        elif role == "bass":
            self._write_bass(instrument, track_name)
        elif role == "chords":
            self._write_chords(instrument, track_name)
        elif role == "pad":
            self._write_pad(instrument, track_name)
        elif role == "arp":
            self._write_arp(instrument)
        elif role == "taiko":
            self._write_taiko(instrument)
        else:
            self._write_melody(instrument, track_name)

    def _add_note(self, instrument, pitch, start, duration, velocity):
        shift = self.rng.randint(-self.humanize, self.humanize)
        start = max(0, start + shift)
        duration = max(60, duration + self.rng.randint(-self.humanize, self.humanize))
        velocity = clamp(velocity + self.mood["velocity"] + self.rng.randint(-5, 5), 24, 124)
        instrument.notes.append(Note(velocity=velocity, pitch=pitch, start=start, end=start + duration))

    def _section_gain(self, bar):
        return self._section_config(bar)["velocity"]

    def _section_density(self, bar):
        return clamp(self.density + self._section_config(bar)["density"], 0.05, 1.0)

    def _section_config(self, bar):
        position = bar / max(1, self.config.bars)
        for section in SECTION_LIBRARY:
            if section["start"] <= position < section["end"]:
                return section

        return {"name": "middle", "velocity": 0, "density": 0.0}

    def _chord_for_bar(self, bar):
        return self.chords[bar % len(self.chords)]

    def _write_chords(self, instrument, track_name):
        instrument_config = INSTRUMENT_LIBRARY.get(track_name, INSTRUMENT_LIBRARY["piano"])
        octave = instrument_config["octave"]
        for bar in range(self.config.bars):
            start = bar * BAR_TICKS
            density = self._section_density(bar)
            velocity = 58 + self._section_gain(bar) + instrument_config["velocity"]
            notes = chord_notes(self._chord_for_bar(bar), octave=octave)
            rhythm = [0, TICKS_PER_BEAT * 2] if density < 0.65 else [0, STEP_TICKS * 3, TICKS_PER_BEAT * 2]
            for offset in rhythm:
                for note in self._voice_chord(notes):
                    self._add_note(instrument, note, start + self._swing(offset), STEP_TICKS * 2, velocity)

    def _write_pad(self, instrument, track_name):
        instrument_config = INSTRUMENT_LIBRARY.get(track_name, INSTRUMENT_LIBRARY["pad"])
        octave = instrument_config["octave"] + self.mood["octave"]
        for bar in range(self.config.bars):
            notes = chord_notes(self._chord_for_bar(bar), octave=octave)
            velocity = 45 + self._section_gain(bar) + instrument_config["velocity"]
            duration = BAR_TICKS * 2 if track_name == "pad" else BAR_TICKS
            for note in notes:
                self._add_note(instrument, note, bar * BAR_TICKS, duration - 40, velocity)

    def _write_bass(self, instrument, track_name):
        instrument_config = INSTRUMENT_LIBRARY.get(track_name, INSTRUMENT_LIBRARY["bass"])
        octave = instrument_config["octave"]
        for bar in range(self.config.bars):
            root, _ = parse_chord(self._chord_for_bar(bar))
            base = 12 * (octave + 1) + root
            density = self._section_density(bar)
            velocity = 72 + self._section_gain(bar) + instrument_config["velocity"]
            pattern = [0, TICKS_PER_BEAT * 2]
            if density > 0.6:
                pattern += [STEP_TICKS * 3, STEP_TICKS * 7]
            for offset in pattern:
                pitch = base + (12 if offset == STEP_TICKS * 7 and self.rng.random() < 0.45 else 0)
                self._add_note(instrument, pitch, bar * BAR_TICKS + self._swing(offset), STEP_TICKS * 2, velocity)

    def _write_arp(self, instrument):
        instrument_config = INSTRUMENT_LIBRARY.get(instrument.name, INSTRUMENT_LIBRARY["pluck"])
        for bar in range(self.config.bars):
            notes = chord_notes(self._chord_for_bar(bar), octave=instrument_config["octave"])
            velocity = 54 + self._section_gain(bar) + instrument_config["velocity"]
            steps = 8 if self._section_density(bar) > 0.55 else 4
            for i in range(steps):
                note = notes[i % len(notes)] + (12 if i > 3 else 0)
                self._add_note(instrument, note, bar * BAR_TICKS + self._swing(i * STEP_TICKS), STEP_TICKS - 40, velocity)

    def _write_melody(self, instrument, track_name):
        instrument_config = INSTRUMENT_LIBRARY.get(track_name, INSTRUMENT_LIBRARY["lead"])
        octave = instrument_config["octave"] + self.mood["octave"]
        for bar in range(4, self.config.bars - 2):
            if self.rng.random() > self._section_density(bar):
                continue
            notes = chord_notes(self._chord_for_bar(bar), octave=octave)
            velocity = 68 + self._section_gain(bar) + instrument_config["velocity"]
            phrase_steps = self._melody_phrase_steps()
            start_step = self.rng.choice([0, 1, 2, 4])
            for i in range(phrase_steps):
                note = self.rng.choice(notes)
                if self.rng.random() < 0.35:
                    note += self._melody_neighbor()
                start = bar * BAR_TICKS + self._swing((start_step + i) * STEP_TICKS)
                self._add_note(instrument, note, start, STEP_TICKS, velocity)

    def _write_drums(self, instrument):
        groove = self.style["drum_groove"]
        if groove == "none":
            return

        for bar in range(self.config.bars):
            base = bar * BAR_TICKS
            gain = self._section_gain(bar)
            self._drum_note(instrument, DRUM_NOTES["kick"], base, 96 + gain)
            if groove in ("four_on_floor", "retro", "rock", "funk"):
                for beat in range(4):
                    self._drum_note(instrument, DRUM_NOTES["kick"], base + beat * TICKS_PER_BEAT, 92 + gain)
            else:
                self._drum_note(instrument, DRUM_NOTES["kick"], base + TICKS_PER_BEAT * 2, 84 + gain)

            for beat in (1, 3):
                snare = DRUM_NOTES["clap"] if groove in ("edm", "four_on_floor") else DRUM_NOTES["snare"]
                self._drum_note(instrument, snare, base + beat * TICKS_PER_BEAT, 86 + gain)

            hat_steps = range(0, 8) if self._section_density(bar) > 0.55 else range(0, 8, 2)
            for step in hat_steps:
                if groove == "trap" and step in (1, 5) and self.rng.random() < 0.7:
                    self._drum_note(instrument, DRUM_NOTES["closed_hat"], base + step * STEP_TICKS + STEP_TICKS // 2, 55 + gain)
                self._drum_note(instrument, DRUM_NOTES["closed_hat"], base + self._swing(step * STEP_TICKS), 50 + gain)

    def _write_taiko(self, instrument):
        for bar in range(self.config.bars):
            base = bar * BAR_TICKS
            gain = self._section_gain(bar)
            for offset in (0, TICKS_PER_BEAT * 2):
                self._add_note(instrument, DRUM_NOTES["tom_low"], base + offset, STEP_TICKS, 84 + gain)

    def _drum_note(self, instrument, pitch, start, velocity):
        self._add_note(instrument, pitch, start, 80, velocity)

    def _swing(self, offset):
        if offset % TICKS_PER_BEAT == STEP_TICKS:
            return int(offset + STEP_TICKS * self.swing)
        return offset

    def _prompt_humanize(self):
        prompt = self.config.prompt.lower()
        base = self.style["humanize"]
        if "tight" in prompt or "quantized" in prompt:
            return max(2, base // 2)
        if "loose" in prompt or "human" in prompt or "live" in prompt:
            return base + 5
        return base

    def _prompt_density(self):
        prompt = self.config.prompt.lower()
        density = 0.0
        if "minimal" in prompt or "sparse" in prompt or "empty" in prompt:
            density -= 0.18
        if "busy" in prompt or "dense" in prompt or "complex" in prompt:
            density += 0.16
        if "club" in prompt or "dance" in prompt or "driving" in prompt:
            density += 0.08
        if "soft" in prompt or "delicate" in prompt:
            density -= 0.06
        return density

    def _voice_chord(self, notes):
        if self.mood["brightness"] < -5:
            return [note - 12 if index == 0 else note for index, note in enumerate(notes)]
        if self.mood["brightness"] > 5:
            return notes + [notes[0] + 12]
        return notes

    def _melody_phrase_steps(self):
        shape = self.style["melody_shape"]
        if shape in ("sparse", "minimal"):
            return self.rng.choice([2, 3, 4])
        if shape in ("hook", "anthem", "minor_hook"):
            return self.rng.choice([4, 5, 6])
        if shape in ("bebop", "syncopated"):
            return self.rng.choice([5, 6, 7])
        return self.rng.choice([3, 4, 5, 6])

    def _melody_neighbor(self):
        shape = self.style["melody_shape"]
        if shape in ("wide", "anthem"):
            return self.rng.choice([-7, -5, 5, 7, 12])
        if shape in ("bebop", "syncopated"):
            return self.rng.choice([-2, 1, 2, 3, 5])
        return self.rng.choice([-2, 2, 5])


def generate_song(config):
    return SongComposer(config).compose()
