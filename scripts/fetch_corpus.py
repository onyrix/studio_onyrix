"""Download and index the optional chord corpus (Chordonomicon, CC BY-NC 4.0).

`make fetch-corpus` / `.\tasks.ps1 fetch-corpus`. The same import can be started from the UI.
Only the statistics index is kept in the corpus folder; the raw CSV is deleted.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import Settings  # noqa: E402
from app.corpus import CORPUS, CorpusStore  # noqa: E402


def main() -> int:
    store = CorpusStore(Settings.from_env().corpus_dir)
    if store.status()["state"] == "ready":
        print(f"{CORPUS['name']}: index already present in {store.dir}")
        return 0
    print(f"{CORPUS['name']} ({CORPUS['licence']}, {CORPUS['size'] / 1e6:.0f} MB): {CORPUS['url']}")
    print(f"Please cite: {CORPUS['attribution']}")
    store.start_import()
    last = ""
    while True:
        status = store.status()
        line = f"{status['state']} {status['progress'] * 100:5.1f}%"
        if line != last:
            print(line, flush=True)
            last = line
        if status["state"] in ("ready", "error"):
            break
        time.sleep(2)
    if status["state"] == "error":
        print(f"Import failed: {status.get('error')}", file=sys.stderr)
        return 1
    print(f"Index saved in {store.index_path} ({status.get('index_size', 0) / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
