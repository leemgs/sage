import json
from pathlib import Path
from scqa.engine import corrupt_state, decide, is_correct, predict_state

DATA = Path(__file__).parents[2] / "paper/data/situationcatch_bench.jsonl"


def items():
    return [json.loads(x) for x in DATA.read_text().splitlines() if x.strip()]


def test_gold_state_complete():
    data = items()
    assert len(data) == 4200
    assert all(is_correct(x, decide(x)) for x in data)


def test_sensor_does_not_copy_gold_slots():
    x = items()[0]
    predicted = predict_state(x)
    assert predicted["state_source"] == "predicted_from_text"
    assert all(set(c) <= {"text", "time", "event", "status", "source",
                          "scope", "actor"} for c in predicted["claims"])


def test_corruption_is_explicit():
    x = corrupt_state(items()[-1])
    assert x["state_source"] == "deliberately_corrupted"
