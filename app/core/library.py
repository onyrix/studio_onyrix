"""Curated chord progression library and song kits (B-56). Pure data, ours (MIT).

Every progression is written in roman numerals relative to the key's own scale (natural minor
in minor keys; `V` is the major dominant) with the harmonic-rhythm syntax of
`core.progression`: `I V vi IV`, `ii7 V7 Imaj7*2`, `(Imaj7 VI7) (ii7 V7)`. They are realized in
any key and time signature with `realize`.

A **song kit** is a set of parts (intro, verse, prechorus, chorus, bridge, outro) designed to
belong together: e.g. a verse on vi that makes the chorus on I sound like a lift, a bridge that
leaves the key's comfort zone before the last chorus.

Tags use fixed English ids; the UI translates them.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from app.core.harmony import chord_from_roman
from app.core.model import Key, Mode
from app.core.progression import ChordEvent, parse_progression
from app.core.timebase import FOUR_FOUR, TimeSignature

MOODS = (
    "bright",
    "uplifting",
    "melancholic",
    "nostalgic",
    "dreamy",
    "romantic",
    "dark",
    "epic",
    "tense",
    "mysterious",
    "groovy",
    "calm",
)
PART_ORDER = ("intro", "verse", "prechorus", "chorus", "bridge", "outro")


@dataclass(frozen=True)
class LibraryProgression:
    id: str
    mode: Mode
    numerals: str
    kinds: frozenset[str] = frozenset()  # section kinds it suits (empty = any)
    genres: frozenset[str] = frozenset()  # genres it suits (empty = any)
    moods: frozenset[str] = frozenset()
    energy: float = 0.5  # 0 calm .. 1 intense


@dataclass(frozen=True)
class SongKit:
    id: str
    mode: Mode
    parts: dict[str, str]  # section kind -> numerals
    genres: frozenset[str] = frozenset()
    moods: frozenset[str] = frozenset()
    bars: dict[str, int] = field(default_factory=dict)  # suggested section length per part


def _p(
    id: str, mode: Mode, numerals: str, kinds: str, genres: str, moods: str, energy: float
) -> LibraryProgression:
    return LibraryProgression(
        id,
        mode,
        numerals,
        frozenset(kinds.split()),
        frozenset(genres.split()),
        frozenset(moods.split()),
        energy,
    )


M, m = Mode.MAJOR, Mode.MINOR

# Ordered by general usefulness: ties in rankings keep this order.
PROGRESSIONS: tuple[LibraryProgression, ...] = (
    # --- major ------------------------------------------------------------------------------
    _p("axis", M, "I V vi IV", "chorus verse", "pop rock country folk", "bright uplifting", 0.7),
    _p(
        "axis_minor_start",
        M,
        "vi IV I V",
        "verse chorus",
        "pop dance-electronic hip-hop",
        "melancholic uplifting",
        0.6,
    ),
    _p("fifties", M, "I vi IV V", "verse", "pop country folk", "nostalgic romantic", 0.5),
    _p(
        "royal_road",
        M,
        "IVmaj7 V iii7 vi",
        "prechorus chorus",
        "pop dance-electronic",
        "dreamy melancholic",
        0.6,
    ),
    _p(
        "canon",
        M,
        "I V vi iii IV I IV V",
        "verse chorus",
        "classical pop folk",
        "romantic nostalgic calm",
        0.4,
    ),
    _p("two_five_one", M, "ii7 V7 Imaj7*2", "verse bridge", "jazz", "calm groovy", 0.4),
    _p(
        "turnaround",
        M,
        "(Imaj7 VI7) (ii7 V7)",
        "verse intro outro",
        "jazz latin",
        "groovy calm",
        0.5,
    ),
    _p(
        "blues12",
        M,
        "I7 I7 I7 I7 IV7 IV7 I7 I7 V7 IV7 I7 V7",
        "verse",
        "blues rock country",
        "groovy",
        0.6,
    ),
    _p("mixolydian", M, "I bVII IV I", "chorus verse", "rock metal punk", "epic bright", 0.8),
    _p(
        "epic_cadence",
        M,
        "I bVI bVII I",
        "chorus outro",
        "rock soundtrack metal",
        "epic uplifting",
        0.9,
    ),
    _p("chromatic_iii", M, "I III IV iv", "verse", "rock pop", "melancholic dreamy", 0.5),
    _p(
        "borrowed_iv",
        M,
        "I iii IV iv",
        "verse bridge",
        "pop folk soundtrack",
        "nostalgic dreamy",
        0.4,
    ),
    _p("lift_to_four", M, "IV I V vi", "chorus bridge", "pop", "uplifting", 0.7),
    _p("plagal_minor", M, "IV iv I*2", "outro bridge", "pop soundtrack", "nostalgic romantic", 0.3),
    _p("climb", M, "I ii iii IV", "prechorus", "pop rock", "uplifting tense", 0.6),
    _p("pre_build", M, "ii IV V*2", "prechorus", "pop rock", "tense uplifting", 0.7),
    _p("pre_axis", M, "IV V vi*2", "prechorus", "pop", "tense melancholic", 0.6),
    _p("bridge_fall", M, "vi V IV V", "bridge", "pop rock", "melancholic", 0.6),
    _p(
        "bridge_escape",
        M,
        "bVI bVII I*2",
        "bridge outro",
        "rock soundtrack pop",
        "epic uplifting",
        0.8,
    ),
    _p(
        "lofi_maj7", M, "Imaj7 IVmaj7", "intro verse", "jazz soundtrack hip-hop", "dreamy calm", 0.2
    ),
    _p("lofi_cycle", M, "ii7 V7 iii7 vi7", "verse chorus", "jazz hip-hop", "dreamy groovy", 0.4),
    _p("funk_vamp", M, "I7*2 IV7*2", "verse", "funk blues", "groovy", 0.7),
    _p(
        "cinematic_mediant",
        M,
        "I bIII bVII IV",
        "chorus bridge",
        "rock soundtrack",
        "epic mysterious",
        0.7,
    ),
    _p("sus_shimmer", M, "I Isus4 I Isus2", "intro outro", "", "calm dreamy", 0.2),
    _p("anthem_cadence", M, "IV V I*2", "outro chorus", "", "uplifting bright", 0.7),
    # --- minor ------------------------------------------------------------------------------
    _p(
        "minor_epic",
        m,
        "i VI III VII",
        "chorus verse",
        "pop rock dance-electronic",
        "epic melancholic",
        0.8,
    ),
    _p("minor_rock", m, "i VII VI VII", "verse chorus", "rock metal", "dark epic", 0.8),
    _p(
        "minor_lift",
        m,
        "VI VII i*2",
        "prechorus chorus",
        "pop rock dance-electronic",
        "epic uplifting",
        0.7,
    ),
    _p(
        "harmonic_minor",
        m,
        "i VI iv V",
        "chorus bridge",
        "pop soundtrack classical",
        "dark tense",
        0.6,
    ),
    _p("andalusian", m, "i VII VI V", "verse chorus", "latin rock flamenco", "tense dark", 0.7),
    _p("minor_folk", m, "i iv v i", "verse", "folk blues", "melancholic calm", 0.3),
    _p("minor_two_five", m, "iiø7 V7 i*2", "verse bridge", "jazz latin", "mysterious calm", 0.4),
    _p(
        "minor_blues12",
        m,
        "i7 i7 i7 i7 iv7 iv7 i7 i7 VI7 V7 i7 V7",
        "verse",
        "blues jazz",
        "dark groovy",
        0.6,
    ),
    _p("minor_pop", m, "i III VII iv", "chorus", "pop hip-hop", "melancholic", 0.6),
    _p("minor_cycle", m, "i iv VII III", "verse", "pop hip-hop", "melancholic nostalgic", 0.5),
    _p("dorian_vamp", m, "i7 IV7", "verse intro", "funk jazz latin", "groovy mysterious", 0.5),
    _p("phrygian", m, "i bII", "verse intro", "metal soundtrack", "tense dark mysterious", 0.8),
    _p("trap_loop", m, "i (VI VII)", "verse chorus", "hip-hop dance-electronic", "dark", 0.7),
    _p("slow_epic", m, "i*2 VI*2 III*2 VII*2", "intro verse", "soundtrack rock", "epic dark", 0.5),
    _p(
        "lament",
        m,
        "i v VI III iv i iv V",
        "verse chorus",
        "classical soundtrack pop",
        "melancholic romantic",
        0.4,
    ),
    _p("minor_hiphop", m, "i VI i VII", "verse", "hip-hop", "dark groovy", 0.6),
    _p("minor_bridge", m, "iv VI VII*2", "prechorus bridge", "pop rock", "tense uplifting", 0.7),
    _p("relative_escape", m, "III VII VI VII", "bridge chorus", "pop rock", "uplifting epic", 0.7),
    _p("minor_pad", m, "i i VI VI", "intro outro", "", "calm dark", 0.2),
    _p(
        "neapolitan",
        m,
        "iv bII V*2",
        "bridge",
        "soundtrack classical metal",
        "tense mysterious",
        0.6,
    ),
)


def _k(id: str, mode: Mode, genres: str, moods: str, **parts: str) -> SongKit:
    return SongKit(id, mode, dict(parts), frozenset(genres.split()), frozenset(moods.split()))


KITS: tuple[SongKit, ...] = (
    _k(
        "pop_lift",
        M,
        "pop dance-electronic",
        "uplifting bright",
        verse="vi IV I V",
        prechorus="ii IV V*2",
        chorus="I V vi IV",
        bridge="IV V iii vi",
        outro="IV V I*2",
    ),
    _k(
        "nostalgic_ballad",
        M,
        "pop folk soundtrack",
        "nostalgic romantic",
        intro="I Isus4 I Isus2",
        verse="I iii IV iv",
        prechorus="vi V IV V",
        chorus="I V vi IV",
        bridge="bVI bVII I*2",
        outro="IV iv I*2",
    ),
    _k(
        "rock_anthem",
        M,
        "rock punk metal",
        "epic bright",
        verse="I bVII IV I",
        prechorus="IV V IV V",
        chorus="I V vi IV",
        bridge="bVI bVII I*2",
        outro="I bVII IV I",
    ),
    _k(
        "neo_soul",
        M,
        "jazz hip-hop funk",
        "dreamy romantic groovy",
        verse="Imaj7 IVmaj7 iii7 vi7",
        prechorus="ii7 iii7 IVmaj7 V7",
        chorus="IVmaj7 V7 iii7 vi7",
        bridge="ii7 V7 Imaj7 VI7",
        outro="IVmaj7 iv7 Imaj7*2",
    ),
    _k(
        "jazz_standard",
        M,
        "jazz latin",
        "calm groovy",
        verse="ii7 V7 Imaj7*2",
        chorus="(Imaj7 VI7) (ii7 V7) (Imaj7 VI7) (ii7 V7)",
        bridge="III7*2 VI7*2 II7*2 V7*2",
        outro="ii7 V7 Imaj7*2",
    ),
    _k(
        "folk_story",
        M,
        "folk country",
        "calm nostalgic",
        verse="I IV I V",
        chorus="IV I V vi",
        bridge="vi IV I V",
        outro="IV V I*2",
    ),
    _k(
        "dream_pop",
        M,
        "pop soundtrack",
        "dreamy calm",
        intro="Imaj7*2 IVmaj7*2",
        verse="Imaj7*2 IVmaj7*2",
        chorus="vi7 IVmaj7 Imaj7 V",
        bridge="bVImaj7*2 IVmaj7*2",
        outro="Imaj7 IVmaj7",
    ),
    _k(
        "dark_pop",
        m,
        "pop dance-electronic",
        "dark melancholic",
        verse="i VI III VII",
        prechorus="iv VI VII*2",
        chorus="VI III VII*2",
        bridge="iv i V*2",
        outro="i VI i*2",
    ),
    _k(
        "epic_cinematic",
        m,
        "soundtrack rock metal",
        "epic dark",
        intro="i*2 VI*2",
        verse="i*2 VI*2 III*2 VII*2",
        prechorus="iv VI VII*2",
        chorus="VI VII i III",
        bridge="iv bII V*2",
        outro="VI VII i*2",
    ),
    _k(
        "andalusian_drama",
        m,
        "latin rock flamenco",
        "tense dark",
        verse="i VII VI V",
        prechorus="iv V",
        chorus="i iv V i",
        bridge="VI III VII V",
        outro="i VII VI V",
    ),
    _k(
        "trap_minor",
        m,
        "hip-hop dance-electronic",
        "dark",
        intro="i*2",
        verse="i (VI VII)",
        chorus="i VI III VII",
        bridge="iv*2 VI V",
        outro="i*2",
    ),
    _k(
        "dorian_groove",
        m,
        "funk jazz latin",
        "groovy mysterious",
        verse="i7 IV7 i7 IV7",
        chorus="iv7 VII7 i7*2",
        bridge="VImaj7 VII7 i7*2",
        outro="i7 IV7",
    ),
)

# Default section length (bars) of each part when a kit creates missing sections.
DEFAULT_BARS = {"intro": 4, "verse": 8, "prechorus": 4, "chorus": 8, "bridge": 8, "outro": 4}


def realize(numerals: str, key: Key, ts: TimeSignature = FOUR_FOUR) -> list[ChordEvent]:
    """Roman-numeral progression -> chord events in `key` and `ts`."""
    return parse_progression(numerals, ts, chord_parser=lambda n: chord_from_roman(n, key))


def length_beats(numerals: str, ts: TimeSignature = FOUR_FOUR) -> int:
    events = realize(numerals, Key(0, Mode.MAJOR), ts)
    return sum(ts.numerator if e.beats is None else e.beats for e in events)


def search(
    mode: Mode,
    kind: str = "",
    genre: str = "",
    moods: Iterable[str] = (),
    bars: int | None = None,
    ts: TimeSignature = FOUR_FOUR,
) -> list[LibraryProgression]:
    """Progressions of `mode`, best match first. Moods filter (any of them must match); kind,
    genre and a length that fits `bars` evenly only rank. Deterministic."""
    wanted = frozenset(moods)
    out = []
    for index, p in enumerate(PROGRESSIONS):
        if p.mode is not mode or (wanted and not wanted & p.moods):
            continue
        rank = 3 * (kind in p.kinds) + 2 * (genre in p.genres) + len(wanted & p.moods)
        if bars is not None:
            length = length_beats(p.numerals, ts)
            total = bars * ts.numerator
            rank += 1 if length <= total and total % length == 0 else -2
        out.append((-rank, index, p))
    return [p for _, _, p in sorted(out, key=lambda item: (item[0], item[1]))]


def kits(mode: Mode | None = None, genre: str = "", moods: Iterable[str] = ()) -> list[SongKit]:
    wanted = frozenset(moods)
    out = []
    for index, kit in enumerate(KITS):
        if mode is not None and kit.mode is not mode:
            continue
        if wanted and not wanted & kit.moods:
            continue
        rank = 2 * (genre in kit.genres) + len(wanted & kit.moods)
        out.append((-rank, index, kit))
    return [k for _, _, k in sorted(out, key=lambda item: (item[0], item[1]))]
