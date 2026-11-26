from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app, is_loopback


def make_client() -> TestClient:
    return TestClient(create_app(Settings(database_url="sqlite://")))


def test_health() -> None:
    response = make_client().get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_index_is_served() -> None:
    response = make_client().get("/")
    assert response.status_code == 200
    assert "js/main.js" in response.text


def test_static_module_is_served() -> None:
    response = make_client().get("/js/lib/i18n.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]


def test_is_loopback() -> None:
    assert is_loopback("127.0.0.1")
    assert is_loopback("localhost")
    assert is_loopback("::1")
    assert not is_loopback("0.0.0.0")
    assert not is_loopback("192.168.1.10")
