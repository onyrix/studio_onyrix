from dataclasses import dataclass, field

from generation.music_config import MOOD_LIBRARY, STYLE_LIBRARY


@dataclass
class SongConfig:
    title: str = "Untitled Onyrix Song"
    bpm: int | None = None
    mood: str = "dreamy"
    style: str = "lofi"
    chords: list[str] = field(default_factory=lambda: ["Cmaj7", "Am", "F", "G"])
    tracks: list[str] = field(default_factory=list)
    bars: int = 32
    prompt: str = ""
    output: str = "output/generated_song.mid"

    def resolved_bpm(self):
        style = STYLE_LIBRARY.get(self.style.lower(), STYLE_LIBRARY["lofi"])
        return self.bpm or style["bpm"]

    def resolved_tracks(self):
        if self.tracks:
            return self.tracks

        style = STYLE_LIBRARY.get(self.style.lower(), STYLE_LIBRARY["lofi"])
        return list(style["tracks"])

    def style_config(self):
        return STYLE_LIBRARY.get(self.style.lower(), STYLE_LIBRARY["lofi"])

    def mood_config(self):
        return MOOD_LIBRARY.get(self.mood.lower(), MOOD_LIBRARY["dreamy"])

    def resolved_chords(self):
        if self.chords:
            return self.chords

        return list(self.style_config()["chords"])
