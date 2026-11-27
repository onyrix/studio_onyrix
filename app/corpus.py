"""Optional chord corpus (Chordonomicon) for the harmonic explorer (B-57).

Downloaded on demand into a git-ignored folder (`Settings.corpus_dir`), never bundled or
committed. The raw CSV (~264 MB) is turned into a compact statistics index
(`core.harmony_stats.HarmonyStats`, gzip JSON) and then deleted. Without the index, statistics
come from our own library, so nothing depends on the download.

Licence: Chordonomicon is CC BY-NC 4.0 (dataset card, checked 2026-11-27): fine for this
personal, non-commercial app; the UI shows the licence and the attribution.
"""

from __future__ import annotations

import csv
import io
import logging
import threading
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

from app.core.corpus_chords import GENRES, estimate_key, numeral, parse_song
from app.core.harmony_stats import HarmonyStats, from_library

log = logging.getLogger(__name__)

CORPUS_ID = "chordonomicon"
CORPUS_URL = (
    "https://huggingface.co/datasets/ailsntua/Chordonomicon/resolve/main/chordonomicon_v2.csv"
)
CORPUS_SIZE = 264_198_044
CORPUS: dict[str, Any] = {
    "id": CORPUS_ID,
    "name": "Chordonomicon",
    "url": CORPUS_URL,
    "size": CORPUS_SIZE,
    "licence": "CC BY-NC 4.0",
    "licence_url": "https://creativecommons.org/licenses/by-nc/4.0/",
    "homepage": "https://huggingface.co/datasets/ailsntua/Chordonomicon",
    "attribution": (
        "Kantarelis, Thomas, Lyberatos, Dervakos, Stamou: CHORDONOMICON: A Dataset of 666,000 "
        "Songs and their Chord Progressions (arXiv:2410.22046)"
    ),
}
INDEX_FILE = "chordonomicon_index.json.gz"
CSV_FILE = ".chordonomicon.csv.part"

ProgressFn = Callable[[float], None]
DownloadFn = Callable[[Path, ProgressFn], None]


def download_csv(dest: Path, progress: ProgressFn) -> None:
    """Stream the corpus CSV from Hugging Face into `dest`. Network access; never in tests."""
    request = urllib.request.Request(CORPUS_URL, headers={"User-Agent": "studio-onyrix"})
    with (
        urllib.request.urlopen(request, timeout=60) as response,  # noqa: S310 (fixed https URL)
        dest.open("wb") as out,
    ):
        total = int(response.headers.get("Content-Length") or CORPUS_SIZE)
        done = 0
        while block := response.read(1 << 20):
            out.write(block)
            done += len(block)
            progress(min(done / total, 1.0))


class _CountingReader(io.RawIOBase):
    """Byte counter around a binary file, for progress while the CSV is parsed."""

    def __init__(self, raw: BinaryIO) -> None:
        self.raw = raw
        self.count = 0

    def readable(self) -> bool:
        return True

    def readinto(self, buffer: Any) -> int:
        data = self.raw.read(len(buffer))
        buffer[: len(data)] = data
        self.count += len(data)
        return len(data)


def build_index(csv_path: Path, progress: ProgressFn | None = None) -> HarmonyStats:
    """Read the corpus CSV into statistics: per song, estimate the key, reduce every chord to a
    numeral and count each tagged section under (mode, kind, genre)."""
    csv.field_size_limit(1 << 26)
    stats = HarmonyStats(source=CORPUS_ID)
    total = max(csv_path.stat().st_size, 1)
    with csv_path.open("rb") as raw:
        counter = _CountingReader(raw)
        text = io.TextIOWrapper(io.BufferedReader(counter), encoding="utf-8", errors="replace")
        for i, row in enumerate(csv.DictReader(text)):
            sections = parse_song(row.get("chords") or "")
            chords = [c for _, cs in sections for c in cs]
            key = estimate_key(chords)
            if key is None:
                continue
            genre = GENRES.get((row.get("main_genre") or "").strip().lower(), "")
            for kind, section in sections:
                numerals: list[str] = []
                for chord in section:
                    n = numeral(chord, key)
                    if not numerals or numerals[-1] != n:
                        numerals.append(n)
                stats.add_section(key.mode, kind, genre, numerals)
            if progress and i % 2000 == 0:
                progress(min(counter.count / total, 1.0))
    stats.prune()
    if progress:
        progress(1.0)
    return stats


@dataclass
class CorpusStatus:
    state: str = "missing"  # missing | downloading | building | ready | error
    progress: float = 0.0
    error: str = ""


class CorpusStore:
    """Owns the corpus folder, the background import and the statistics in use."""

    def __init__(self, directory: str | Path, download: DownloadFn = download_csv) -> None:
        self.dir = Path(directory)
        self._download = download
        self._lock = threading.Lock()
        self._status = CorpusStatus(state="ready" if self.index_path.is_file() else "missing")
        self._stats: HarmonyStats | None = None
        self._thread: threading.Thread | None = None

    @property
    def index_path(self) -> Path:
        return self.dir / INDEX_FILE

    def status(self) -> dict[str, Any]:
        with self._lock:
            s = self._status
            out: dict[str, Any] = {"state": s.state, "progress": round(s.progress, 4)}
            if s.error:
                out["error"] = s.error
        if s.state == "ready" and self.index_path.is_file():
            out["index_size"] = self.index_path.stat().st_size
        out["source"] = self.stats().source
        out["corpus"] = CORPUS
        return out

    def _set(self, **changes: Any) -> None:
        with self._lock:
            for name, value in changes.items():
                setattr(self._status, name, value)

    def start_import(self) -> bool:
        """Download and index in a background thread. False if one is already running."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return False
            self._status = CorpusStatus(state="downloading")
            self._thread = threading.Thread(target=self._import, name="corpus-import", daemon=True)
            self._thread.start()
            return True

    def wait(self, timeout: float | None = None) -> None:
        thread = self._thread
        if thread is not None:
            thread.join(timeout)

    def _import(self) -> None:
        csv_path = self.dir / CSV_FILE
        try:
            self.dir.mkdir(parents=True, exist_ok=True)
            self._download(csv_path, lambda p: self._set(progress=p))
            self._set(state="building", progress=0.0)
            stats = build_index(csv_path, lambda p: self._set(progress=p))
            stats.save(self.index_path)
            with self._lock:
                self._stats = stats
                self._status = CorpusStatus(state="ready", progress=1.0)
        except Exception as exc:  # reported to the UI; the library statistics stay in use
            log.exception("corpus import failed")
            self._set(state="error", error=f"{type(exc).__name__}: {exc}")
        finally:
            csv_path.unlink(missing_ok=True)

    def delete(self) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError("an import is running")
            self.index_path.unlink(missing_ok=True)
            self._stats = None
            self._status = CorpusStatus()

    def stats(self) -> HarmonyStats:
        """Corpus statistics when imported, otherwise the library's (both cached)."""
        with self._lock:
            if self._stats is not None:
                return self._stats
        stats: HarmonyStats | None = None
        if self.index_path.is_file():
            try:
                stats = HarmonyStats.load(self.index_path)
            except (OSError, ValueError) as exc:
                log.warning("cannot read the corpus index: %s", exc)
        if stats is None:
            stats = _library_stats()
        with self._lock:
            self._stats = stats
        return stats


_LIBRARY_STATS: HarmonyStats | None = None


def _library_stats() -> HarmonyStats:
    global _LIBRARY_STATS
    if _LIBRARY_STATS is None:
        _LIBRARY_STATS = from_library()
    return _LIBRARY_STATS
