"""FastAPI application factory and CLI entry point (`python -m app.main`)."""

from __future__ import annotations

import argparse
import ipaddress
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.api import clips, corpus, export, generate, harmony, health, projects, soundfonts
from app.config import WEB_DIR, Settings
from app.corpus import CorpusStore
from app.db.base import Base
from app.db.session import MEMORY_URLS, make_engine, make_session_factory
from app.gen.engine import Engine, MidiGptEngine
from app.gen.jobs import JobManager
from app.soundfonts import SoundfontStore


def create_app(settings: Settings | None = None, engine: Engine | None = None) -> FastAPI:
    """Build the app. `engine` defaults to midigpt, loaded lazily on first generation."""
    settings = settings or Settings.from_env()
    db_engine = make_engine(settings.database_url)
    if settings.database_url in MEMORY_URLS:
        Base.metadata.create_all(db_engine)  # tests / throwaway runs; files use Alembic
    jobs = JobManager()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        jobs.shutdown()
        db_engine.dispose()

    app = FastAPI(title="Studio Onyrix", version=__version__, lifespan=lifespan)
    app.state.settings = settings
    app.state.session_factory = make_session_factory(db_engine)
    app.state.engine = engine or MidiGptEngine(
        settings.model_name, settings.fallback_model_name, device=settings.device
    )
    app.state.jobs = jobs
    app.state.candidates = {}
    app.state.soundfonts = SoundfontStore(settings.soundfont_dir)
    app.state.corpus = CorpusStore(settings.corpus_dir)

    api = APIRouter(prefix="/api")
    for module in (health, projects, clips, generate, harmony, corpus, export, soundfonts):
        api.include_router(module.router)
    app.include_router(api)

    # Mounted last so /api routes take precedence. Static files are served as-is (no build).
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
    return app


def is_loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def cli(argv: list[str] | None = None) -> None:
    import uvicorn

    from app.db.migrate import upgrade_to_head

    env = Settings.from_env()
    parser = argparse.ArgumentParser(prog="onyrix", description="Run Studio Onyrix.")
    parser.add_argument("--host", default=env.host, help="bind address (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=env.port)
    args = parser.parse_args(argv)

    if not is_loopback(args.host):
        print(
            f"WARNING: binding to {args.host}. There is NO authentication: anyone on the "
            "network can read and modify your projects.",
            file=sys.stderr,
        )

    upgrade_to_head(env.database_url)
    uvicorn.run(create_app(env), host=args.host, port=args.port)


if __name__ == "__main__":
    cli()
