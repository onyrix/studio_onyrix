"""Local LLM client: Ollama over HTTP with the standard library (CLAUDE.md 6.6).

Never a remote service by default: the URL is a setting (`ONYRIX_LLM_URL`, default
`http://127.0.0.1:11434`). When Ollama is not running every caller falls back to rules.
Prompts and answers are not logged.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any


class LlmUnavailable(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, url: str, model: str, timeout: float = 20.0) -> None:
        self.url = url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._checked_at = 0.0
        self._available = False
        self._models: list[str] = []

    def _request(self, method: str, path: str, body: Any = None, timeout: float = 2.0) -> Any:
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            f"{self.url}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json", "User-Agent": "studio-onyrix"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 (local URL from settings)
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise LlmUnavailable(str(exc)) from exc

    def status(self, max_age: float = 30.0) -> dict[str, Any]:
        """Is Ollama reachable and is the configured model installed? (cached `max_age` s)"""
        now = time.monotonic()
        if now - self._checked_at > max_age:
            self._checked_at = now
            try:
                tags = self._request("GET", "/api/tags", timeout=0.5)
                self._models = [str(m.get("name", "")) for m in tags.get("models", [])]
                self._available = True
            except LlmUnavailable:
                self._available, self._models = False, []
        has_model = any(
            m == self.model or m.split(":")[0] == self.model.split(":")[0] for m in self._models
        )
        return {
            "available": self._available and has_model,
            "running": self._available,
            "model": self.model,
            "models": list(self._models),
        }

    def chat_json(self, system: str, user: str, schema: dict[str, Any]) -> Any:
        """One chat turn with structured (JSON schema) output; returns the parsed JSON."""
        if not self.status()["available"]:
            raise LlmUnavailable("Ollama or the model is not available")
        answer = self._request(
            "POST",
            "/api/chat",
            {
                "model": self.model,
                "stream": False,
                "format": schema,
                "options": {"temperature": 0},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=self.timeout,
        )
        try:
            return json.loads(answer["message"]["content"])
        except (KeyError, TypeError, ValueError) as exc:
            raise LlmUnavailable(f"unreadable answer: {exc}") from exc
