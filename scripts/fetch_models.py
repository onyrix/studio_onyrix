"""Pre-download model weights into the Hugging Face cache (`make fetch-models`)."""

from __future__ import annotations

import sys

MODELS = ("prism_medium", "yellow_medium")


def main() -> int:
    from midigpt.inference import InferenceEngine

    failed = 0
    for name in sys.argv[1:] or MODELS:
        try:
            InferenceEngine.from_pretrained(name, device="cpu")
            print(f"{name}: ok")
        except Exception as exc:
            failed += 1
            print(f"{name}: FAILED ({type(exc).__name__}: {exc})")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
