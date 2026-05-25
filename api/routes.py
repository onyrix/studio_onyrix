from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from generation.composer import generate_song
from generation.music_config import INSTRUMENT_LIBRARY, MOOD_LIBRARY, STYLE_LIBRARY
from generation.project import PROJECT_NAME, PROJECT_VERSION
from generation.song_config import SongConfig

router = APIRouter()


@router.get("/config")
def config():
    return {
        "project": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "styles": STYLE_LIBRARY,
        "moods": MOOD_LIBRARY,
        "instruments": INSTRUMENT_LIBRARY,
    }


class GenerateRequest(BaseModel):
    title: str = "Onyrix Song"
    bpm: Optional[int] = Field(default=None, ge=40, le=220)
    mood: str = "dreamy"
    style: str = "lofi"
    chords: list[str] = Field(default_factory=lambda: ["Cmaj7", "Am", "F", "G"])
    tracks: list[str] = Field(default_factory=list)
    bars: int = Field(default=32, ge=4, le=128)
    prompt: str = ""
    output: str = "output/generated_song.mid"


@router.post("/generate")
def generate(data: GenerateRequest):
    try:
        if data.style.lower() not in STYLE_LIBRARY:
            styles = ", ".join(sorted(STYLE_LIBRARY))
            raise ValueError(f"Unknown style '{data.style}'. Available styles: {styles}")

        out_path = generate_song(
            SongConfig(
                title=data.title,
                bpm=data.bpm,
                mood=data.mood,
                style=data.style,
                chords=data.chords,
                tracks=data.tracks,
                bars=data.bars,
                prompt=data.prompt,
                output=data.output,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"status": "ok", "path": out_path}
