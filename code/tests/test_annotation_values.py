"""Codebook validation in annotation_cli (synthetic packets only)."""
import csv
import importlib.util
from pathlib import Path

import pytest

CODE = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("annotation_cli", CODE / "annotation_cli.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)

ROW = {"blind_id": "b1", "item_id": "x-1", "question": "q", "evidence": "e",
       "action": "ANSWER", "answer": "Juno", "temporal_state": "relevant",
       "modality": "confirmed", "scope": "global", "source_status": "reliable",
       "observer_state": "shared", "world": "actual", "notes": ""}


def write(tmp, changes, encoding="utf-8"):
    for i, change in enumerate(changes, 1):
        row = {**ROW, **change}
        with (tmp / f"annotator_{i}.csv").open("w", newline="", encoding=encoding) as f:
            w = csv.DictWriter(f, fieldnames=list(ROW))
            w.writeheader()
            w.writerow(row)


def test_case_and_whitespace_are_normalised(tmp_path):
    write(tmp_path, [{}, {"action": "answer ", "answer": " juno"}, {"world": "Actual"}],
          encoding="utf-8-sig")
    packets, _ = cli.load_completed_annotations(tmp_path)
    assert {p[1][0]["action"] for p in packets} == {"ANSWER"}
    assert {p[1][0]["answer"] for p in packets} == {"juno"}
    assert {p[1][0]["world"] for p in packets} == {"actual"}


def test_value_outside_codebook_fails_closed(tmp_path):
    write(tmp_path, [{}, {"scope": "local"}, {}])
    with pytest.raises(SystemExit, match="Invalid scope value 'local'"):
        cli.load_completed_annotations(tmp_path)


def test_worked_examples_are_not_annotation_items():
    """Annotators must not see filled-in labels for items they will rate."""
    packets = CODE.parent / "paper" / "annotation_packets"
    rated = {r["item_id"] for r in csv.DictReader(
        (packets / "annotator_1.csv").open(encoding="utf-8"))}
    examples = {r["item_id"] for r in csv.DictReader(
        (packets / "EXAMPLE_annotator_filled.csv").open(encoding="utf-8"))}
    assert examples and not (examples & rated)


def test_simulated_disagreements_stay_inside_codebook(tmp_path):
    import json
    from types import SimpleNamespace
    src = tmp_path / "items.jsonl"
    src.write_text("".join(json.dumps({"id": f"temporal-{i}", "category": "temporal",
                                       "question": "Who?", "claims": [],
                                       "gold_action": "ANSWER", "gold_answer": "Ari"}) + "\n"
                           for i in range(20)))
    out = tmp_path / "sim"
    cli.simulate_personas(SimpleNamespace(input=str(src), out=str(out), seed=1,
                                          disagreement_rate=1.0))
    cli.load_completed_annotations(out)  # raises if any value is outside the codebook
