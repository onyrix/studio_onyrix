"""Standard MIDI file export via mido (type 1, PPQ 480).

Layout: track 0 is the conductor (name, tempo, time signature); then one MIDI track per project
track with its name and GM program. Drums use channel 10 (index 9); melodic tracks take the
other channels in order (more than 15 melodic tracks share channels cyclically).
"""

from __future__ import annotations

import io
from collections.abc import Sequence
from dataclasses import dataclass

import mido

from app.core.model import Note
from app.core.timebase import PPQ, TimeSignature, bpm_to_us_per_quarter

DRUM_CHANNEL = 9
MELODIC_CHANNELS = tuple(c for c in range(16) if c != DRUM_CHANNEL)


@dataclass(frozen=True)
class ExportTrack:
    name: str
    program: int
    is_drum: bool
    notes: tuple[Note, ...]  # absolute ticks from the start of the song


def _channels(tracks: Sequence[ExportTrack]) -> list[int]:
    out = []
    melodic = 0
    for track in tracks:
        if track.is_drum:
            out.append(DRUM_CHANNEL)
        else:
            out.append(MELODIC_CHANNELS[melodic % len(MELODIC_CHANNELS)])
            melodic += 1
    return out


def _to_delta(events: list[tuple[int, int, mido.Message]]) -> list[mido.Message]:
    """events: (absolute tick, order, message); order puts note_off before note_on at a tick."""
    events.sort(key=lambda e: (e[0], e[1]))
    out = []
    now = 0
    for tick, _, msg in events:
        out.append(msg.copy(time=tick - now))
        now = tick
    return out


# Loop markers understood by SpessaSynth (and other players): CC116 = loop start, CC117 = loop
# end. They are "undefined" controllers, so they do not change the sound.
LOOP_START_CC = 116
LOOP_END_CC = 117


def build_midi(
    name: str,
    bpm: float,
    ts: TimeSignature,
    tracks: Sequence[ExportTrack],
    loop_ticks: int | None = None,
) -> mido.MidiFile:
    """`loop_ticks`: when set, add loop markers from 0 to that tick (playback files only), which
    also makes the file last exactly that long even if the last note ends earlier."""
    mid = mido.MidiFile(type=1, ticks_per_beat=PPQ)
    head = [
        mido.MetaMessage("track_name", name=name, time=0),
        mido.MetaMessage("set_tempo", tempo=bpm_to_us_per_quarter(bpm), time=0),
        mido.MetaMessage(
            "time_signature", numerator=ts.numerator, denominator=ts.denominator, time=0
        ),
    ]
    markers: list[tuple[int, int, mido.Message]] = []
    if loop_ticks is not None:
        markers = [
            (0, 0, mido.Message("control_change", channel=0, control=LOOP_START_CC, value=0)),
            (
                loop_ticks,
                0,
                mido.Message("control_change", channel=0, control=LOOP_END_CC, value=0),
            ),
        ]
    conductor = mido.MidiTrack(
        [*head, *_to_delta(markers), mido.MetaMessage("end_of_track", time=0)]
    )
    mid.tracks.append(conductor)

    for track, channel in zip(tracks, _channels(tracks), strict=True):
        head = [mido.MetaMessage("track_name", name=track.name, time=0)]
        if not track.is_drum:
            head.append(mido.Message("program_change", channel=channel, program=track.program))
        events: list[tuple[int, int, mido.Message]] = []
        for n in track.notes:
            events.append(
                (n.t, 1, mido.Message("note_on", channel=channel, note=n.p, velocity=n.v))
            )
            events.append(
                (n.end, 0, mido.Message("note_off", channel=channel, note=n.p, velocity=0))
            )
        body = _to_delta(events)
        mid.tracks.append(mido.MidiTrack([*head, *body, mido.MetaMessage("end_of_track", time=0)]))
    return mid


def to_bytes(mid: mido.MidiFile) -> bytes:
    buffer = io.BytesIO()
    mid.save(file=buffer)
    return buffer.getvalue()
