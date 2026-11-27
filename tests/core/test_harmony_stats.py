from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from app.core.harmony import chord_from_roman
from app.core.harmony_stats import HarmonyStats, bucket, from_library, reduce_numerals
from app.core.model import Key, Mode

M = Mode.MAJOR


def toy() -> HarmonyStats:
    stats = HarmonyStats(source="test")
    for _ in range(20):
        stats.add_section(M, "chorus", "pop", ["I", "V", "vi", "IV", "I", "V", "vi", "IV"])
    for _ in range(5):
        stats.add_section(M, "verse", "rock", ["I", "bVII", "IV", "I"])
    stats.add_section(M, "verse", "", ["I", "bIII", "bVI", "bII"])
    return stats


def test_buckets_and_counts() -> None:
    stats = toy()
    assert stats.sections == 26
    assert stats.bigrams[bucket(M, "chorus", "pop")]["I"]["V"] == 40
    assert stats.bigrams[bucket(M)]["I"]["bVII"] == 5
    assert bucket(M, "chorus", "pop") not in stats.trigrams  # trigrams: kind and overall only
    assert stats.trigrams[bucket(M, "chorus")]["V vi"]["IV"] == 40
    assert stats.loops[bucket(M, "chorus")]["I V vi IV"] == 40


def test_distribution_is_a_probability_and_follows_the_context() -> None:
    stats = toy()
    dist = stats.distribution(M, "chorus", "pop", ["I", "V"])
    assert abs(sum(dist.values()) - 1) < 1e-9
    assert max(dist, key=dist.__getitem__) == "vi"
    assert stats.distribution(Mode.MINOR, "", "", ["i"]) == {}


def test_surprise_ranks_idioms_below_oddities() -> None:
    stats = toy()
    common = stats.surprise(M, "chorus", "pop", ["I", "V", "vi", "IV"])
    odd = stats.surprise(M, "chorus", "pop", ["I", "bIII", "bVI", "bII"])
    unseen = stats.surprise(M, "chorus", "pop", ["I", "#iv°", "bII", "III+"])
    assert common < odd < unseen
    assert stats.surprise(M, "", "", ["I"]) == 0.0


def test_prune_drops_rare_counts() -> None:
    stats = toy()
    stats.prune(min_count=2)
    assert "bIII" not in stats.bigrams[bucket(M)].get("I", {})
    assert stats.bigrams[bucket(M)]["I"]["V"] == 40


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    stats = toy()
    path = tmp_path / "index.json.gz"
    stats.save(path)
    loaded = HarmonyStats.load(path)
    assert loaded == stats


def test_generate_follows_audacity_and_is_reproducible() -> None:
    stats = from_library()
    calm = stats.generate(M, "chorus", "pop", length=4, audacity=0.0, seed=1)
    wild = stats.generate(M, "chorus", "pop", length=4, audacity=1.0, seed=1)
    assert calm and wild
    assert calm == stats.generate(M, "chorus", "pop", length=4, audacity=0.0, seed=1)
    assert all(len(seq) == 4 for seq, _ in calm + wild)
    assert calm[0][1] <= wild[0][1]


@settings(max_examples=30, deadline=None)
@given(
    st.sampled_from(list(Mode)),
    st.sampled_from(["", "verse", "chorus", "bridge", "prechorus", "outro"]),
    st.integers(2, 8),
    st.floats(0, 1),
    st.integers(0, 10_000),
)
def test_generated_numerals_are_valid_and_never_repeat(
    mode: Mode, kind: str, length: int, audacity: float, seed: int
) -> None:
    stats = from_library()
    for seq, bits in stats.generate(mode, kind, "", length, audacity, seed, n=3):
        assert bits >= 0
        assert all(a != b for a, b in zip(seq, seq[1:] + seq[:1], strict=True))
        for n in seq:
            chord_from_roman(n, Key(0, mode))


def test_library_stats_cover_both_modes() -> None:
    stats = from_library()
    assert stats.source == "library"
    assert "I" in stats.vocabulary(M)
    assert "i" in stats.vocabulary(Mode.MINOR)
    assert stats.common_loops(M, "chorus", "pop", 3)


def test_reduce_numerals() -> None:
    assert reduce_numerals("ii7 V7 Imaj7*2", Key(0, M)) == ["ii", "V7", "I"]
    assert reduce_numerals("iiø7 V7 i*2", Key(0, Mode.MINOR)) == ["ii°", "V7", "i"]
