from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai.pipeline import MidiAIPipeline

router = APIRouter()


class GenerateRequest(BaseModel):
    midi_path: str = "input.mid"
    output_path: str = "output/generated.mid"
    style: Optional[str] = None
    chords: Optional[list[str]] = None
    max_new_tokens: int = Field(default=512, ge=1, le=2048)


@router.post("/generate")
def generate(data: GenerateRequest):
    try:
        pipeline = MidiAIPipeline()
        out_path = pipeline.generate_from_midi(
            data.midi_path,
            out_path=data.output_path,
            style=data.style,
            chords=data.chords,
            max_new_tokens=data.max_new_tokens,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"status": "ok", "path": out_path}
