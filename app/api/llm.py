"""Local LLM status for the UI (CLAUDE.md 6.6)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.gen.llm import OllamaClient

router = APIRouter(tags=["llm"])


@router.get("/llm/status")
def llm_status(request: Request) -> dict[str, Any]:
    """Is the local Ollama running, and is the configured model installed?"""
    client: OllamaClient = request.app.state.llm
    return {**client.status(), "url": client.url}
