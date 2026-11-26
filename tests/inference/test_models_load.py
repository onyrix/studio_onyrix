"""Model smoke tests. Run with `make test-infer`; downloads weights on first run."""

from typing import Any

import pytest

pytestmark = pytest.mark.inference

midigpt_inference = pytest.importorskip("midigpt.inference")


@pytest.fixture(scope="module", params=["yellow_medium", "prism_medium"])
def engine(request: pytest.FixtureRequest) -> Any:
    return midigpt_inference.InferenceEngine.from_pretrained(request.param, device="cpu")


def test_engine_reports_attributes_and_windows(engine: Any) -> None:
    import json

    enc = json.loads(engine._tokenizer._vocab.config().to_json())
    assert 4 in (enc.get("num_bars_map") or [])
    assert engine._analyzer.attribute_sizes()


def test_generates_valid_4_bar_bass(engine: Any) -> None:
    from midigpt import Bar, Note, Score, Track

    chords = [[57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]]
    piano = Track(bars=[Bar(notes=[Note(p, 80, 0, 1900) for p in c]) for c in chords], instrument=0)
    bass = Track(bars=[Bar() for _ in chords], instrument=33)
    score = Score(tracks=[piano, bass], resolution=480, tempo=600000)
    request = midigpt_inference.GenerationRequest(
        tracks=[
            midigpt_inference.TrackPrompt(id=0, bars=[]),
            midigpt_inference.TrackPrompt(id=1, bars=[0, 1, 2, 3]),
        ],
        config=midigpt_inference.InferenceConfig(seed=7, model_dim=4, top_p=0.95),
    )
    result = engine.session(score, request).run()
    notes = [n for bar in result.tracks[1].bars for n in bar.notes]
    assert len(result.tracks[1].bars) == 4
    assert notes, "expected some bass notes"
    assert all(0 <= n.pitch <= 127 and n.duration_ticks > 0 for n in notes)
