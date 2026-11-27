"""Application settings: environment variables (prefix ONYRIX_) over defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "web"
MAX_CANDIDATES = 8


def _env(name: str, default: str) -> str:
    return os.environ.get(f"ONYRIX_{name}", default)


@dataclass(frozen=True)
class Settings:
    database_url: str = f"sqlite:///{(ROOT_DIR / 'onyrix.db').as_posix()}"
    model_name: str = "prism_medium"
    fallback_model_name: str = "yellow_medium"
    device: str = "auto"  # auto | cpu | cuda | mps
    soundfont_dir: str = str(ROOT_DIR / "data" / "soundfonts")
    corpus_dir: str = str(ROOT_DIR / "data" / "corpus")
    n_candidates: int = 4
    host: str = "127.0.0.1"
    port: int = 8000
    locale: str = "it"

    def __post_init__(self) -> None:
        if not 1 <= self.n_candidates <= MAX_CANDIDATES:
            raise ValueError(
                f"n_candidates must be in 1..{MAX_CANDIDATES}, got {self.n_candidates}"
            )

    @classmethod
    def from_env(cls) -> Settings:
        defaults = cls()
        return cls(
            database_url=_env("DATABASE_URL", defaults.database_url),
            model_name=_env("MODEL", defaults.model_name),
            fallback_model_name=_env("FALLBACK_MODEL", defaults.fallback_model_name),
            device=_env("DEVICE", defaults.device),
            soundfont_dir=_env("SOUNDFONT_DIR", defaults.soundfont_dir),
            corpus_dir=_env("CORPUS_DIR", defaults.corpus_dir),
            n_candidates=int(_env("N_CANDIDATES", str(defaults.n_candidates))),
            host=_env("HOST", defaults.host),
            port=int(_env("PORT", str(defaults.port))),
            locale=_env("LOCALE", defaults.locale),
        )
