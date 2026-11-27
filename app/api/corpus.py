"""Optional chord corpus: status, on-demand import (download + indexing), removal."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response

from app.corpus import CorpusStore

router = APIRouter(tags=["corpus"])


def store(request: Request) -> CorpusStore:
    s: CorpusStore = request.app.state.corpus
    return s


@router.get("/corpus")
def corpus_status(request: Request) -> dict[str, Any]:
    """State (missing / downloading / building / ready / error), progress 0..1, the statistics
    source in use ("library" or "chordonomicon") and the corpus licence."""
    return store(request).status()


@router.post("/corpus/download", status_code=202)
def corpus_download(request: Request) -> dict[str, Any]:
    """Start downloading and indexing the corpus in the background; poll GET /corpus."""
    s = store(request)
    if not s.start_import():
        raise HTTPException(409, "an import is already running")
    return s.status()


@router.delete("/corpus", status_code=204)
def corpus_delete(request: Request) -> Response:
    try:
        store(request).delete()
    except RuntimeError as exc:
        raise HTTPException(409, str(exc)) from exc
    return Response(status_code=204)
