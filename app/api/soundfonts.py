"""Sound banks for browser playback: list, upload, serve, choose the active one, delete."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.soundfonts import DEFAULT_BANK, SUGGESTED_BANKS, Bank, BankError, SoundfontStore
from app.soundfonts import download_default as download_default_bank

router = APIRouter(tags=["soundfonts"])


def store(request: Request) -> SoundfontStore:
    s: SoundfontStore = request.app.state.soundfonts
    return s


def bank_out(bank: Bank, active: str | None) -> dict[str, Any]:
    return {**bank.__dict__, "active": bank.id == active}


class ActiveIn(BaseModel):
    id: str


@router.get("/soundfonts")
def list_banks(request: Request) -> dict[str, Any]:
    s = store(request)
    active = s.active
    return {
        "active": active,
        "banks": [bank_out(b, active) for b in s.list()],
        "default": DEFAULT_BANK,
        "suggested": SUGGESTED_BANKS,
    }


@router.post("/soundfonts", status_code=201)
async def upload_bank(request: Request, filename: str = Query(min_length=1)) -> dict[str, Any]:
    """Raw upload: the request body is the bank file (no multipart, no extra dependency)."""
    s = store(request)
    try:
        bank = await s.save_stream(filename, request.stream())
    except BankError as exc:
        raise HTTPException(422, str(exc)) from exc
    return bank_out(bank, s.active)


@router.post("/soundfonts/default", status_code=201)
def download_default(request: Request) -> dict[str, Any]:
    """Download the default bank (MuseScore General, MIT) from its official mirror."""
    s = store(request)
    try:
        bank = download_default_bank(s)
    except BankError as exc:
        raise HTTPException(502, f"downloaded file is not valid: {exc}") from exc
    except OSError as exc:
        raise HTTPException(502, f"download failed: {exc}") from exc
    return bank_out(bank, s.active)


@router.get("/soundfonts/{bank_id}/file")
def bank_file(bank_id: str, request: Request) -> FileResponse:
    try:
        path = store(request).path(bank_id)
    except (BankError, FileNotFoundError) as exc:
        raise HTTPException(404, f"bank {bank_id} not found") from exc
    return FileResponse(path, media_type="application/octet-stream", filename=bank_id)


@router.put("/soundfonts/active")
def set_active(body: ActiveIn, request: Request) -> dict[str, Any]:
    try:
        store(request).set_active(body.id)
    except (BankError, FileNotFoundError) as exc:
        raise HTTPException(404, f"bank {body.id} not found") from exc
    return list_banks(request)


@router.delete("/soundfonts/{bank_id}", status_code=204)
def delete_bank(bank_id: str, request: Request) -> Response:
    try:
        store(request).delete(bank_id)
    except (BankError, FileNotFoundError) as exc:
        raise HTTPException(404, f"bank {bank_id} not found") from exc
    return Response(status_code=204)
