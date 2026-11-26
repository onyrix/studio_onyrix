"""FastAPI application factory and CLI entry point (`python -m app.main`)."""

from __future__ import annotations

import argparse
import ipaddress
import sys

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.api import health
from app.config import WEB_DIR, Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(title="Studio Onyrix", version=__version__)
    app.state.settings = settings

    api = APIRouter(prefix="/api")
    api.include_router(health.router)
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
