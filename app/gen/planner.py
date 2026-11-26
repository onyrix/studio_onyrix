"""Planner interface (CLAUDE.md section 6.6). Implementations arrive in M5.

The generator must never depend on a specific planner.
"""

from __future__ import annotations

from typing import Any, Protocol, TypedDict

from app.core.model import Key


class Plan(TypedDict):
    chord_grid: list[dict[str, Any]]
    sections: list[dict[str, Any]]
    per_bar_controls: list[dict[str, Any]]


class Planner(Protocol):
    def plan(self, genre: str, key: Key, bpm: float, structure: list[str]) -> Plan: ...
