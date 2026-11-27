"""Chord-transition statistics, surprise and a progression generator (B-57 / B-58). Pure.

Statistics are counted over reduced roman numerals (`core.corpus_chords.numeral`) per bucket
`(mode, kind, genre)`; "" means "any". They come from the Chordonomicon corpus when the user has
imported it (`app.corpus`), otherwise from our own library (`from_library`), so every feature
built on them works offline.

- `distribution`: P(next | two previous chords), an interpolation of trigram, genre bigram,
  bigram and unigram estimates (whatever the buckets hold).
- `surprise`: mean information (bits) of a looping progression's transitions; low = idiomatic,
  high = unusual for the mode / section / genre.
- `generate`: samples many candidates with a temperature set by the "audacity" (0 idiomatic ..
  1 adventurous) and keeps those whose surprise sits closest to the audacity target.
"""

from __future__ import annotations

import gzip
import json
import math
import random
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core import library
from app.core.corpus_chords import CorpusChord, family_of_quality, numeral
from app.core.model import Key, Mode
from app.core.progression import ChordEvent

FORMAT_VERSION = 1
_ANY = ""
TONIC = {Mode.MAJOR: "I", Mode.MINOR: "i"}


def bucket(mode: Mode, kind: str = _ANY, genre: str = _ANY) -> str:
    return f"{mode.value}|{kind}|{genre}"


@dataclass
class HarmonyStats:
    source: str = "library"
    sections: int = 0
    unigrams: dict[str, Counter[str]] = field(default_factory=dict)
    bigrams: dict[str, dict[str, Counter[str]]] = field(default_factory=dict)
    trigrams: dict[str, dict[str, Counter[str]]] = field(default_factory=dict)
    starts: dict[str, Counter[str]] = field(default_factory=dict)
    loops: dict[str, Counter[str]] = field(default_factory=dict)

    # ---- counting ------------------------------------------------------------------------

    def add_section(self, mode: Mode, kind: str, genre: str, numerals: Sequence[str]) -> None:
        """Count one section's chord sequence (consecutive repeats already merged)."""
        if not numerals:
            return
        self.sections += 1
        # Unigrams, starts, bigrams and loops: per kind x genre, per kind, per genre and overall.
        # Trigrams (sparser, bigger): per kind and overall only.
        buckets = {bucket(mode)}
        trigram_buckets = {bucket(mode)}
        if kind:
            buckets.add(bucket(mode, kind))
            trigram_buckets.add(bucket(mode, kind))
        if genre:
            buckets.add(bucket(mode, _ANY, genre))
        if kind and genre:
            buckets.add(bucket(mode, kind, genre))
        for b in buckets:
            self.unigrams.setdefault(b, Counter()).update(numerals)
            self.starts.setdefault(b, Counter())[numerals[0]] += 1
            pairs = self.bigrams.setdefault(b, {})
            for a, c in zip(numerals, numerals[1:], strict=False):
                pairs.setdefault(a, Counter())[c] += 1
            if len(numerals) >= 4:
                loops = self.loops.setdefault(b, Counter())
                for i in range(len(numerals) - 3):
                    loops[" ".join(numerals[i : i + 4])] += 1
        for b in trigram_buckets:
            triples = self.trigrams.setdefault(b, {})
            for a, c, d in zip(numerals, numerals[1:], numerals[2:], strict=False):
                triples.setdefault(f"{a} {c}", Counter())[d] += 1

    def prune(self, min_count: int = 2, max_loops: int = 300) -> None:
        """Drop rare counts (noise in user-made chord charts) to keep the index small."""

        def keep(counter: Counter[str]) -> Counter[str]:
            return Counter({k: v for k, v in counter.items() if v >= min_count})

        for table in (self.bigrams, self.trigrams):
            for b, contexts in table.items():
                table[b] = {ctx: kept for ctx, c in contexts.items() if (kept := keep(c))}
        for b, counter in self.loops.items():
            self.loops[b] = Counter(dict(keep(counter).most_common(max_loops)))

    # ---- persistence ---------------------------------------------------------------------

    def to_json(self) -> dict[str, Any]:
        return {
            "version": FORMAT_VERSION,
            "source": self.source,
            "sections": self.sections,
            "unigrams": self.unigrams,
            "bigrams": self.bigrams,
            "trigrams": self.trigrams,
            "starts": self.starts,
            "loops": self.loops,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> HarmonyStats:
        if data.get("version") != FORMAT_VERSION:
            raise ValueError("unsupported statistics format")

        def counters(d: dict[str, dict[str, int]]) -> dict[str, Counter[str]]:
            return {k: Counter(v) for k, v in d.items()}

        return cls(
            source=str(data["source"]),
            sections=int(data["sections"]),
            unigrams=counters(data["unigrams"]),
            bigrams={b: counters(v) for b, v in data["bigrams"].items()},
            trigrams={b: counters(v) for b, v in data["trigrams"].items()},
            starts=counters(data["starts"]),
            loops=counters(data["loops"]),
        )

    def save(self, path: Path) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with gzip.open(tmp, "wt", encoding="utf-8") as f:
            json.dump(self.to_json(), f, separators=(",", ":"))
        tmp.replace(path)

    @classmethod
    def load(cls, path: Path) -> HarmonyStats:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return cls.from_json(json.load(f))

    # ---- probabilities -------------------------------------------------------------------

    def vocabulary(self, mode: Mode) -> list[str]:
        return sorted(self.unigrams.get(bucket(mode), Counter()))

    def distribution(
        self, mode: Mode, kind: str, genre: str, context: Sequence[str]
    ) -> dict[str, float]:
        """P(next | context): weighted mix of the estimates available for these buckets."""
        parts: list[tuple[float, Counter[str] | None]] = []
        if len(context) >= 2:
            key = f"{context[-2]} {context[-1]}"
            parts.append((0.45, _first(self.trigrams, [bucket(mode, kind), bucket(mode)], key)))
        if context:
            prev = context[-1]
            if genre:
                g = self.bigrams.get(bucket(mode, kind, genre), {}).get(prev)
                parts.append((0.25, g or self.bigrams.get(bucket(mode, _ANY, genre), {}).get(prev)))
            parts.append((0.2, _first(self.bigrams, [bucket(mode, kind), bucket(mode)], prev)))
        uni = self.unigrams.get(bucket(mode, kind)) or self.unigrams.get(bucket(mode))
        parts.append((0.1, uni))
        mixed: dict[str, float] = {}
        total_weight = 0.0
        for weight, counter in parts:
            if not counter:
                continue
            total = sum(counter.values())
            total_weight += weight
            for chord, n in counter.items():
                mixed[chord] = mixed.get(chord, 0.0) + weight * n / total
        if not total_weight:
            return {}
        return {k: v / total_weight for k, v in mixed.items()}

    def surprise(self, mode: Mode, kind: str, genre: str, numerals: Sequence[str]) -> float:
        """Mean bits per transition of a looping progression (the last chord leads back to the
        first). Unknown transitions cost as much as the rarest known one, plus one bit."""
        seq = _merge_repeats(numerals)
        if len(seq) < 2:
            return 0.0
        looped = seq + seq[:2]
        vocab = max(2, len(self.vocabulary(mode)))
        floor = 1.0 / (vocab * 2)
        bits = []
        for i in range(2, len(looped)):
            dist = self.distribution(mode, kind, genre, looped[i - 2 : i])
            bits.append(-math.log2(max(dist.get(looped[i], 0.0), floor)))
        return sum(bits) / len(bits)

    def common_loops(self, mode: Mode, kind: str, genre: str, n: int) -> list[tuple[str, int]]:
        for b in (bucket(mode, kind, genre), bucket(mode, kind), bucket(mode)):
            counter = self.loops.get(b)
            if counter:
                return counter.most_common(n)
        return []

    # ---- generation ----------------------------------------------------------------------

    def generate(
        self,
        mode: Mode,
        kind: str = "",
        genre: str = "",
        length: int = 4,
        audacity: float = 0.3,
        seed: int = 0,
        n: int = 5,
        tries: int = 60,
    ) -> list[tuple[list[str], float]]:
        """`n` distinct progressions of `length` chords with their surprise, the ones closest to
        the audacity target first. Deterministic for a given seed."""
        audacity = min(max(audacity, 0.0), 1.0)
        rng = random.Random(seed)
        temperature = 0.3 + 2.2 * audacity
        top_k = 3 + int(audacity * 25)
        candidates: dict[tuple[str, ...], float] = {}
        for _ in range(tries):
            seq = self._sample(mode, kind, genre, length, temperature, top_k, rng)
            if len(seq) == length and tuple(seq) not in candidates:
                candidates[tuple(seq)] = self.surprise(mode, kind, genre, seq)
        if not candidates:
            return []
        values = sorted(candidates.values())
        low, high = values[0], values[-1]
        target = low + (high - low) * audacity
        ranked = sorted(candidates.items(), key=lambda kv: (abs(kv[1] - target), kv[0]))
        return [(list(seq), bits) for seq, bits in ranked[:n]]

    def _sample(
        self,
        mode: Mode,
        kind: str,
        genre: str,
        length: int,
        temperature: float,
        top_k: int,
        rng: random.Random,
    ) -> list[str]:
        start = _first_counter(
            self.starts, [bucket(mode, kind, genre), bucket(mode, kind), bucket(mode)]
        )
        if not start:
            return []
        seq = [_pick({k: float(v) for k, v in start.items()}, temperature, top_k, rng)]
        while len(seq) < length:
            dist = self.distribution(mode, kind, genre, seq)
            dist.pop(seq[-1], None)  # no immediate repeats: the data has none either
            if len(seq) == length - 1:
                dist.pop(seq[0], None)  # the loop goes back to the first chord: avoid a repeat
            if not dist:
                break
            seq.append(_pick(dist, temperature, top_k, rng))
        return seq


def _first(
    table: dict[str, dict[str, Counter[str]]], buckets: Iterable[str], key: str
) -> Counter[str] | None:
    for b in buckets:
        found = table.get(b, {}).get(key)
        if found:
            return found
    return None


def _first_counter(table: dict[str, Counter[str]], buckets: Iterable[str]) -> Counter[str] | None:
    for b in buckets:
        if table.get(b):
            return table[b]
    return None


def _pick(dist: dict[str, float], temperature: float, top_k: int, rng: random.Random) -> str:
    items = sorted(dist.items(), key=lambda kv: (-kv[1], kv[0]))[:top_k]
    weights = [p ** (1.0 / temperature) for _, p in items]
    return rng.choices([k for k, _ in items], weights=weights)[0]


def _merge_repeats(numerals: Sequence[str]) -> list[str]:
    out: list[str] = []
    for n in numerals:
        if not out or out[-1] != n:
            out.append(n)
    while len(out) > 1 and out[-1] == out[0]:
        out.pop()  # a loop that ends on its first chord repeats it
    return out


SURPRISE_LOW, SURPRISE_HIGH = 1.5, 6.0  # bits mapped to 0 and 1 by `surprise_level`


def surprise_level(bits: float) -> float:
    """Surprise in bits -> 0 (idiomatic) .. 1 (very unusual), for the UI meter."""
    return min(1.0, max(0.0, (bits - SURPRISE_LOW) / (SURPRISE_HIGH - SURPRISE_LOW)))


def numerals_of(events: Sequence[ChordEvent], key: Key) -> list[str]:
    """Chord events -> the reduced statistics vocabulary (durations ignored)."""
    return [
        numeral(CorpusChord(e.chord.root, family_of_quality(e.chord.quality)), key) for e in events
    ]


def reduce_numerals(numerals: str, key: Key) -> list[str]:
    """Library numerals (with sevenths, durations) -> the reduced statistics vocabulary."""
    reduced = numerals_of(library.realize(numerals, key), key)
    return _merge_repeats(reduced) if len(reduced) > 1 else reduced


def from_library() -> HarmonyStats:
    """Statistics from our own library and kits: the offline default."""
    stats = HarmonyStats(source="library")
    for entry in library.PROGRESSIONS:
        key = Key(0, entry.mode)
        seq = reduce_numerals(entry.numerals, key)
        looped = seq + seq[:3]  # progressions loop: count the way back to the start too
        for kind in entry.kinds or {_ANY}:
            for genre in entry.genres or {_ANY}:
                stats.add_section(entry.mode, kind, genre, looped)
    for kit in library.KITS:
        key = Key(0, kit.mode)
        for kind, numerals in kit.parts.items():
            seq = reduce_numerals(numerals, key)
            for genre in kit.genres or {_ANY}:
                stats.add_section(kit.mode, kind, genre, seq + seq[:3])
    return stats
