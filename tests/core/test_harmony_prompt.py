import pytest

from app.core.harmony_prompt import (
    HarmonyIntent,
    KeywordHarmonyInterpreter,
    intent_schema,
    normalize_text,
    validate_intent,
)
from app.core.model import Mode

interpret = KeywordHarmonyInterpreter().interpret


def test_italian_request() -> None:
    intent = interpret("Un ritornello malinconico ma che si apre, tipo pop, con le settime")
    assert intent.moods == ("uplifting", "melancholic")
    assert (intent.genre, intent.kind, intent.operators) == ("pop", "chorus", ("sevenths",))


def test_english_request() -> None:
    intent = interpret("dark cinematic bridge in minor, very experimental, 6 chords")
    assert set(intent.moods) == {"dark", "epic"}
    assert (intent.kind, intent.mode, intent.audacity, intent.length) == (
        "bridge",
        Mode.MINOR,
        0.95,
        6,
    )


@pytest.mark.parametrize(
    ("text", "field", "value"),
    [
        ("giro semplice e orecchiabile", "audacity", 0.1),
        ("qualcosa di originale", "audacity", 0.5),
        ("strofa sognante in maggiore", "mode", Mode.MAJOR),
        ("pre-ritornello teso", "kind", "prechorus"),
        ("quattro accordi rap", "length", 4),
        ("intro calma lo-fi", "genre", ""),
        ("intro calma lo-fi", "moods", ("dreamy", "calm")),
        ("finale con modulazione su di un tono", "operators", ("step_up",)),
        ("hip hop cupo", "genre", "hip-hop"),
        ("Malinconìa, perché no?", "moods", ("melancholic",)),
    ],
)
def test_keywords(text: str, field: str, value: object) -> None:
    assert getattr(interpret(text), field) == value


def test_nothing_recognised_is_empty() -> None:
    assert interpret("qwerty").empty
    assert interpret("").empty


def test_validate_drops_unknown_values_and_clamps() -> None:
    intent = validate_intent(
        {
            "moods": ["dark", "angry", "epic", "calm", "bright"],
            "mode": "dorian",
            "genre": ["jazz", "pop"],
            "section": "chorus",
            "audacity": 3,
            "length": 40,
            "operators": ["sevenths", "explode", "sevenths"],
        }
    )
    assert intent == HarmonyIntent(
        moods=("dark", "epic", "calm"),
        genre="jazz",
        kind="chorus",
        audacity=1.0,
        length=8,
        operators=("sevenths",),
    )
    assert validate_intent("not a dict") == HarmonyIntent()
    assert validate_intent({"audacity": True, "length": "4"}).audacity is None


def test_schema_lists_every_allowed_value() -> None:
    schema = intent_schema()
    assert "melancholic" in schema["properties"]["moods"]["items"]["enum"]
    assert set(schema["required"]) == set(HarmonyIntent().as_dict())


def test_normalize_text() -> None:
    assert normalize_text("Più  Malinconìa,  PERCHÉ?") == " piu malinconia perche "
