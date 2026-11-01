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


def test_no_constant_answer_or_recency_shortcut():
    """v0.2 invariant: within each category no single gold answer exceeds 50%,
    and where claim order could decide the answer the decisive claim is the
    newest claim in exactly half of the items."""
    from collections import Counter
    data = items()
    for cat in {x["category"] for x in data}:
        group = [x for x in data if x["category"] == cat]
        top = Counter((x["gold_action"], x["gold_answer"]) for x in group).most_common(1)[0][1]
        assert top <= len(group) / 2, cat
    newest = lambda x: max(x["claims"], key=lambda c: c["time"])
    source = [x for x in data if x["category"] == "source_conflict"]
    assert sum(newest(x)["source"] == "official" for x in source) * 2 == len(source)
    world = [x for x in data if x["category"] == "counterfactual"]
    assert sum(newest(x)["scope"] == "counterfactual" for x in world) * 2 == len(world)
    temporal = [x for x in data if x["category"] == "temporal"]
    assert sum(newest(x)["actor"] == x["gold_answer"] for x in temporal) * 2 == len(temporal)
