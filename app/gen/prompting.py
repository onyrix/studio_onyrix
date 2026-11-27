"""Prompt interpretation: local LLM when available, keywords otherwise (CLAUDE.md 6.7).

The LLM only fills a fixed structure (JSON schema); `validate_intent` keeps what is valid. If
Ollama is down, slow or answers nonsense, the keyword interpreter answers instead, so a prompt
always gets a result offline.
"""

from __future__ import annotations

import logging

from app.core.harmony_prompt import (
    GENRES,
    PROGRESSION_OPERATORS,
    HarmonyIntent,
    KeywordHarmonyInterpreter,
    intent_schema,
    validate_intent,
)
from app.core.library import MOODS, PART_ORDER
from app.gen.llm import LlmUnavailable, OllamaClient

log = logging.getLogger(__name__)

HARMONY_SYSTEM = f"""You turn a musician's request for a chord progression (Italian or English)
into parameters for a progression generator. Answer only with the JSON object.
- moods: up to 3 of {", ".join(MOODS)}.
- mode: "major", "minor" or null when not stated or implied.
- genre: one of {", ".join(GENRES)}, or "" when not stated.
- kind: the song section, one of {", ".join(PART_ORDER)}, or "".
- audacity: 0 = the most common progressions, 1 = unusual ones; null when not stated.
- length: number of chords, or null.
- operators: transformations explicitly asked for, among {", ".join(PROGRESSION_OPERATORS)}
  (sevenths = richer seventh chords, tonic_pedal = chords over the tonic in the bass,
  negative_harmony = mirrored harmony, double_time / half_time = faster / slower chord changes,
  step_up = modulate a whole tone up).
Do not invent chords."""


def interpret_harmony(text: str, client: OllamaClient | None) -> tuple[HarmonyIntent, str]:
    """(intent, source) where source is "ollama" or "keywords"."""
    keywords = KeywordHarmonyInterpreter().interpret(text)
    if client is None:
        return keywords, "keywords"
    try:
        answer = client.chat_json(HARMONY_SYSTEM, text, intent_schema())
    except LlmUnavailable as exc:
        log.info("LLM not used: %s", exc)
        return keywords, "keywords"
    intent = validate_intent(answer)
    if intent.empty:
        return keywords, "keywords"
    return intent, "ollama"
