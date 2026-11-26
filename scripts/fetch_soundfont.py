"""Download the default sound bank (MuseScore General, MIT) into the bank folder.

`make fetch-soundfont` / `.\\tasks.ps1 fetch-soundfont`. Other banks are imported from the UI.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import Settings  # noqa: E402
from app.soundfonts import DEFAULT_BANK, SoundfontStore, download_default  # noqa: E402


def main() -> int:
    store = SoundfontStore(Settings.from_env().soundfont_dir)
    if any(b.id == DEFAULT_BANK["id"] for b in store.list()):
        print(f"{DEFAULT_BANK['name']}: already present in {store.dir}")
        return 0
    print(
        f"Downloading {DEFAULT_BANK['name']} ({DEFAULT_BANK['licence']}) from {DEFAULT_BANK['url']}"
    )
    bank = download_default(store)
    print(f"Saved {bank.id} ({bank.size / 1e6:.1f} MB) in {store.dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
