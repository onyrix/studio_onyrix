"""Prompt -> progressions, with the keyword interpreter and with a fake local Ollama."""

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.gen.llm import OllamaClient


def _project(client: TestClient, **fields: object) -> int:
    body = {"name": "Song", "key_tonic": 0, "key_mode": "major", "genre": "pop", **fields}
    project_id: int = client.post("/api/projects", json=body).json()["id"]
    return project_id


def test_prompt_with_keywords(client: TestClient) -> None:
    pid = _project(client)
    text = "ritornello malinconico in minore con settime, 4 accordi"
    out = client.post("/api/harmony/prompt", json={"project_id": pid, "text": text}).json()
    assert out["source"] == "keywords"
    assert out["intent"]["moods"] == ["melancholic"]
    assert out["intent"]["operators"] == ["sevenths"]
    assert out["key"] == {"tonic": 0, "mode": "minor", "changed": True}
    origins = {p["origin"] for p in out["progressions"]}
    assert origins == {"library", "generated"}
    # Sevenths applied: the tonic of C minor became Cm7.
    assert any("Cm7" in p["chord_text"] for p in out["progressions"])
    generated = [p for p in out["progressions"] if p["origin"] == "generated"]
    assert all(len(p["chords"]) == 4 for p in generated)


def test_prompt_without_matches_still_answers(client: TestClient) -> None:
    pid = _project(client)
    out = client.post("/api/harmony/prompt", json={"project_id": pid, "text": "qwerty"}).json()
    assert out["progressions"]
    assert out["key"]["changed"] is False


def test_llm_status_when_ollama_is_not_running(client: TestClient) -> None:
    status = client.get("/api/llm/status").json()
    assert (status["available"], status["running"]) == (False, False)


class FakeOllama(BaseHTTPRequestHandler):
    answer: dict[str, Any] = {}
    requests: list[dict[str, Any]] = []

    def log_message(self, *args: Any) -> None:
        pass

    def _send(self, payload: Any) -> None:
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self._send({"models": [{"name": "qwen2.5:7b"}]})

    def do_POST(self) -> None:
        length = int(self.headers["Content-Length"])
        FakeOllama.requests.append(json.loads(self.rfile.read(length)))
        self._send({"message": {"content": json.dumps(FakeOllama.answer)}})


@pytest.fixture
def ollama() -> Iterator[str]:
    server = HTTPServer(("127.0.0.1", 0), FakeOllama)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    FakeOllama.requests.clear()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


def test_prompt_with_a_local_llm(client: TestClient, ollama: str) -> None:
    client.app.state.llm = OllamaClient(ollama, "qwen2.5:7b")  # type: ignore[attr-defined]
    FakeOllama.answer = {
        "moods": ["dreamy", "furious"],
        "mode": None,
        "genre": "jazz",
        "kind": "verse",
        "audacity": 0.6,
        "length": 3,
        "operators": [],
    }
    pid = _project(client)
    text = "qualcosa di sospeso e notturno"
    out = client.post("/api/harmony/prompt", json={"project_id": pid, "text": text}).json()
    assert out["source"] == "ollama"
    assert out["intent"]["moods"] == ["dreamy"]  # "furious" is not a known mood: dropped
    assert (out["intent"]["genre"], out["intent"]["length"]) == ("jazz", 3)
    sent = FakeOllama.requests[-1]
    assert sent["format"]["type"] == "object" and sent["stream"] is False
    assert sent["messages"][-1]["content"] == text
    status = client.get("/api/llm/status").json()
    assert status["available"] is True


def test_nonsense_from_the_llm_falls_back_to_keywords(client: TestClient, ollama: str) -> None:
    client.app.state.llm = OllamaClient(ollama, "qwen2.5:7b")  # type: ignore[attr-defined]
    FakeOllama.answer = {"chords": ["C", "G"]}  # not our structure
    pid = _project(client)
    out = client.post("/api/harmony/prompt", json={"project_id": pid, "text": "strofa cupa"}).json()
    assert out["source"] == "keywords"
    assert out["intent"]["moods"] == ["dark"]
