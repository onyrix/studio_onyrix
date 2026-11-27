"""Corpus import with a synthetic CSV in the Chordonomicon format and a fake downloader."""

import csv
from collections.abc import Callable
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.harmony_stats import bucket
from app.core.model import Mode
from app.corpus import INDEX_FILE, CorpusStore, build_index

FIELDS = ["id", "chords", "release_date", "genres", "decade", "rock_genre", "artist_id",
          "main_genre", "spotify_song_id", "spotify_artist_id"]  # fmt: skip
SONGS = [
    ("<intro_1> C <verse_1> Amin F C G <chorus_1> C G Amin F C G Amin F", "pop"),
    ("<verse_1> D A Bmin G D A Bmin G <chorus_1> G A D D", "rock"),
    ("<verse_1> Emin C G D Emin C G D <bridge_1> C D Emin Emin", "rap"),
    ("<solo_1> C F <verse_1> Esus4 E Amin <outro_1> Fno3d Gno3d Cno3d", ""),
]


def write_csv(path: Path, copies: int = 3) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for i in range(copies):
            for j, (chords, genre) in enumerate(SONGS):
                writer.writerow({"id": i * 10 + j, "chords": chords, "main_genre": genre})


def fake_download(copies: int = 3) -> Callable[[Path, Callable[[float], None]], None]:
    def download(dest: Path, progress: Callable[[float], None]) -> None:
        write_csv(dest, copies)
        progress(1.0)

    return download


def test_build_index_counts_sections_by_key_kind_and_genre(tmp_path: Path) -> None:
    path = tmp_path / "c.csv"
    write_csv(path)
    progress: list[float] = []
    stats = build_index(path, progress.append)
    assert stats.source == "chordonomicon"
    assert progress[-1] == 1.0
    major = Mode.MAJOR
    # Song 1 in C: chorus I V vi IV (x2), counted three times.
    assert stats.bigrams[bucket(major, "chorus", "pop")]["I"]["V"] == 6
    # Song 2 in D: the same numerals in another key.
    assert stats.bigrams[bucket(major, "verse", "rock")]["I"]["V"] == 6
    # Song 3 is in E minor: i VI III VII, genre rap -> hip-hop.
    assert stats.bigrams[bucket(Mode.MINOR, "verse", "hip-hop")]["i"]["VI"] == 6
    # Solo sections are skipped.
    assert all("|solo|" not in b for b in stats.unigrams)


def test_store_imports_in_background_and_falls_back_to_the_library(tmp_path: Path) -> None:
    store = CorpusStore(tmp_path / "corpus", download=fake_download())
    assert store.status()["state"] == "missing"
    assert store.stats().source == "library"
    assert store.start_import()
    store.wait(30)
    status = store.status()
    assert status["state"] == "ready", status
    assert status["source"] == "chordonomicon"
    assert (tmp_path / "corpus" / INDEX_FILE).is_file()
    assert not list((tmp_path / "corpus").glob("*.part"))  # the raw CSV is removed
    # A new store (e.g. after a restart) reads the saved index.
    again = CorpusStore(tmp_path / "corpus", download=fake_download())
    assert again.status()["state"] == "ready"
    assert again.stats().source == "chordonomicon"
    again.delete()
    assert again.status()["state"] == "missing"
    assert again.stats().source == "library"


def test_failed_import_reports_an_error(tmp_path: Path) -> None:
    def broken(dest: Path, progress: Callable[[float], None]) -> None:
        raise OSError("network down")

    store = CorpusStore(tmp_path, download=broken)
    store.start_import()
    store.wait(30)
    status = store.status()
    assert status["state"] == "error"
    assert "network down" in status["error"]
    assert store.stats().source == "library"


@pytest.fixture
def corpus_client(client: TestClient, tmp_path: Path) -> TestClient:
    client.app.state.corpus = CorpusStore(tmp_path / "c", download=fake_download())  # type: ignore[attr-defined]
    return client


def test_corpus_api(corpus_client: TestClient) -> None:
    status = corpus_client.get("/api/corpus").json()
    assert (status["state"], status["source"]) == ("missing", "library")
    assert status["corpus"]["licence"] == "CC BY-NC 4.0"
    assert corpus_client.post("/api/corpus/download").status_code == 202
    corpus_client.app.state.corpus.wait(30)  # type: ignore[attr-defined]
    assert corpus_client.get("/api/corpus").json()["state"] == "ready"
    assert corpus_client.delete("/api/corpus").status_code == 204
    assert corpus_client.get("/api/corpus").json()["state"] == "missing"
