"""Programmatic Alembic upgrade, used at startup and in tests."""

from __future__ import annotations

from alembic import command
from alembic.config import Config

from app.config import ROOT_DIR


def alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT_DIR / "app" / "db" / "migrations"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    return cfg


def upgrade_to_head(database_url: str) -> None:
    command.upgrade(alembic_config(database_url), "head")
