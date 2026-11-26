"""Sound bank storage (SF2 / SF3 / DLS) for browser playback.

Banks live in a git-ignored folder (`Settings.soundfont_dir`) and are never committed. The app
downloads only banks whose licence allows it (the default, MuseScore General, MIT); any other
bank is imported by the user. The active bank id is stored in `.active` inside the folder.
"""

from __future__ import annotations

import os
import re
import tempfile
import urllib.request
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass
from pathlib import Path

EXTENSIONS = {".sf2": "sf2", ".sf3": "sf3", ".dls": "dls"}
MAX_BYTES = 2 * 1024**3  # 2 GiB
ACTIVE_FILE = ".active"

DEFAULT_BANK = {
    "id": "MuseScore_General.sf3",
    "name": "MuseScore General",
    "url": "https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf3",
    "licence": "MIT",
    "licence_url": "https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General_License.md",
}

# Shown in the UI with their licence notes; the user downloads and imports them.
SUGGESTED_BANKS = [
    {
        "name": "GeneralUser GS 2.0",
        "licence": "GeneralUser GS License v2.0",
        "licence_kind": "permissive",
        "url": "https://schristiancollins.com/generaluser.php",
    },
    {
        "name": "FluidR3_GM",
        "licence": "MIT",
        "licence_kind": "permissive",
        "url": "https://musescore.org/en/handbook/soundfonts",
    },
    {
        "name": "Timbres of Heaven",
        "licence": "Timbres of Heaven licence",
        "licence_kind": "non_commercial",
        "url": "http://midkar.com/soundfonts/",
    },
]


class BankError(ValueError):
    pass


@dataclass(frozen=True)
class Bank:
    id: str
    name: str
    format: str
    size: int


def sniff_format(head: bytes) -> str | None:
    """'sfbk' RIFF = SF2 or SF3 (Vorbis samples inside the same container); 'DLS ' RIFF = DLS."""
    if len(head) < 12 or head[:4] != b"RIFF":
        return None
    kind = head[8:12]
    if kind == b"sfbk":
        return "sf2"
    if kind == b"DLS ":
        return "dls"
    return None


def safe_id(filename: str) -> str:
    """File name reduced to a safe id (keeps the extension); raises on unsupported types."""
    base = os.path.basename(filename.replace("\\", "/")).strip()
    stem, ext = os.path.splitext(base)
    ext = ext.lower()
    if ext not in EXTENSIONS:
        raise BankError(f"unsupported file type {ext or '(none)'}: use .sf2, .sf3 or .dls")
    stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", stem).strip(" ._") or "bank"
    return f"{stem[:120]}{ext}"


class SoundfontStore:
    def __init__(self, directory: str | Path) -> None:
        self.dir = Path(directory)

    def _ensure(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)

    def path(self, bank_id: str) -> Path:
        if bank_id != safe_id(bank_id):
            raise BankError(f"invalid bank id {bank_id!r}")
        path = self.dir / bank_id
        if not path.is_file():
            raise FileNotFoundError(bank_id)
        return path

    def list(self) -> list[Bank]:
        if not self.dir.is_dir():
            return []
        out = []
        for p in sorted(self.dir.iterdir(), key=lambda p: p.name.lower()):
            ext = p.suffix.lower()
            if p.is_file() and ext in EXTENSIONS and not p.name.startswith("."):
                out.append(
                    Bank(p.name, p.stem.replace("_", " "), EXTENSIONS[ext], p.stat().st_size)
                )
        return out

    @property
    def active(self) -> str | None:
        marker = self.dir / ACTIVE_FILE
        if marker.is_file():
            bank_id = marker.read_text(encoding="utf-8").strip()
            if (self.dir / bank_id).is_file():
                return bank_id
        banks = self.list()
        return banks[0].id if banks else None  # fall back to the first bank

    def set_active(self, bank_id: str) -> None:
        self.path(bank_id)  # validates
        self._ensure()
        (self.dir / ACTIVE_FILE).write_text(bank_id, encoding="utf-8")

    def delete(self, bank_id: str) -> None:
        path = self.path(bank_id)
        was_active = self.active == bank_id
        path.unlink()
        if was_active:
            (self.dir / ACTIVE_FILE).unlink(missing_ok=True)

    def _finish(self, tmp: Path, filename: str, written: int) -> Bank:
        with tmp.open("rb") as f:
            kind = sniff_format(f.read(12))
        if kind is None:
            tmp.unlink(missing_ok=True)
            raise BankError("not a SoundFont (SF2/SF3) or DLS file")
        bank_id = safe_id(filename)
        target = self.dir / bank_id
        os.replace(tmp, target)
        if self.active is None or len(self.list()) == 1:
            self.set_active(bank_id)
        return Bank(
            bank_id, target.stem.replace("_", " "), EXTENSIONS[target.suffix.lower()], written
        )

    async def save_stream(self, filename: str, chunks: AsyncIterator[bytes]) -> Bank:
        safe_id(filename)  # reject bad names before reading the body
        self._ensure()
        fd, name = tempfile.mkstemp(dir=self.dir, prefix=".upload-")
        tmp = Path(name)
        written = 0
        try:
            with os.fdopen(fd, "wb") as out:
                async for chunk in chunks:
                    written += len(chunk)
                    if written > MAX_BYTES:
                        raise BankError("file too large (max 2 GiB)")
                    out.write(chunk)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
        return self._finish(tmp, filename, written)

    def save_iter(self, filename: str, chunks: Iterator[bytes]) -> Bank:
        safe_id(filename)
        self._ensure()
        fd, name = tempfile.mkstemp(dir=self.dir, prefix=".download-")
        tmp = Path(name)
        written = 0
        try:
            with os.fdopen(fd, "wb") as out:
                for chunk in chunks:
                    written += len(chunk)
                    if written > MAX_BYTES:
                        raise BankError("file too large (max 2 GiB)")
                    out.write(chunk)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
        return self._finish(tmp, filename, written)


def download_default(store: SoundfontStore) -> Bank:
    """Download MuseScore General (MIT) into the store. Network access; never called in tests."""
    request = urllib.request.Request(DEFAULT_BANK["url"], headers={"User-Agent": "studio-onyrix"})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 (fixed https URL)

        def chunks() -> Iterator[bytes]:
            while block := response.read(1 << 20):
                yield block

        return store.save_iter(DEFAULT_BANK["id"], chunks())
