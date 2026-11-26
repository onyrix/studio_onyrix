import pytest
from fastapi.testclient import TestClient

from app.soundfonts import BankError, safe_id, sniff_format

SF2 = b"RIFF\x10\x00\x00\x00sfbkLIST" + b"\x00" * 64
DLS = b"RIFF\x10\x00\x00\x00DLS LIST" + b"\x00" * 64


def upload(client: TestClient, name: str, body: bytes) -> dict:  # type: ignore[type-arg]
    response = client.post(
        f"/api/soundfonts?filename={name}",
        content=body,
        headers={"Content-Type": "application/octet-stream"},
    )
    return {"status": response.status_code, "json": response.json()}


def test_sniff_and_ids() -> None:
    assert sniff_format(SF2) == "sf2"
    assert sniff_format(DLS) == "dls"
    assert sniff_format(b"RIFF\x00\x00\x00\x00WAVE") is None
    assert sniff_format(b"MThd") is None
    assert safe_id("My Bank (v2).SF2") == "My Bank _v2.sf2"
    assert safe_id("..\\..\\evil.sf3") == "evil.sf3"
    with pytest.raises(BankError):
        safe_id("song.mid")


def test_upload_list_serve_activate_delete(client: TestClient) -> None:
    assert client.get("/api/soundfonts").json()["banks"] == []

    first = upload(client, "Piano Bank.sf2", SF2)
    assert first["status"] == 201
    assert first["json"] == {
        "id": "Piano Bank.sf2",
        "name": "Piano Bank",
        "format": "sf2",
        "size": len(SF2),
        "active": True,  # the first bank becomes active
    }
    assert upload(client, "kit.dls", DLS)["status"] == 201

    listing = client.get("/api/soundfonts").json()
    assert [b["id"] for b in listing["banks"]] == ["kit.dls", "Piano Bank.sf2"]
    assert listing["active"] == "Piano Bank.sf2"
    assert listing["default"]["licence"] == "MIT"
    assert any("Timbres" in s["name"] for s in listing["suggested"])

    served = client.get("/api/soundfonts/kit.dls/file")
    assert served.status_code == 200 and served.content == DLS

    assert client.put("/api/soundfonts/active", json={"id": "kit.dls"}).json()["active"] == (
        "kit.dls"
    )
    assert client.delete("/api/soundfonts/kit.dls").status_code == 204
    assert client.get("/api/soundfonts").json()["active"] == "Piano Bank.sf2"  # fallback


def test_rejects_invalid_files(client: TestClient) -> None:
    assert upload(client, "song.mid", b"MThd")["status"] == 422
    not_a_bank = upload(client, "fake.sf2", b"RIFF\x00\x00\x00\x00WAVEdata")
    assert not_a_bank["status"] == 422
    assert "not a SoundFont" in not_a_bank["json"]["detail"]
    assert client.get("/api/soundfonts").json()["banks"] == []  # nothing left behind


def test_unknown_or_unsafe_ids(client: TestClient) -> None:
    assert client.get("/api/soundfonts/missing.sf2/file").status_code == 404
    assert client.get("/api/soundfonts/..%5Csecret.sf2/file").status_code == 404
    assert client.put("/api/soundfonts/active", json={"id": "nope.sf2"}).status_code == 404
    assert client.delete("/api/soundfonts/nope.sf2").status_code == 404
