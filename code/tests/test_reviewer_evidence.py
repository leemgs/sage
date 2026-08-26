import csv
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


CODE = Path(__file__).parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, CODE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


annotation = load("annotation_cli")
multifamily = load("audit_multifamily")


def write_mock_packets(directory):
    """Fill every field with unmistakable synthetic values for harness tests."""
    directory.mkdir()
    fields = ["blind_id", "item_id", "question", "evidence", *annotation.SLOTS]
    for annotator in range(3):
        with (directory / f"annotator_{annotator + 1}.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for item in range(2):
                row = {field: f"MOCK_{field}" for field in fields}
                row.update(blind_id=f"mock-{annotator}-{item}", item_id=f"mock-{item}",
                           question=f"MOCK question {item}", evidence="[]",
                           notes="SYNTHETIC TEST VALUE - NOT HUMAN DATA")
                writer.writerow(row)


def test_ideal_mock_human_packets_score_all_slots(tmp_path):
    packets = tmp_path / "packets"
    write_mock_packets(packets)
    output = tmp_path / "agreement.json"
    annotation.score(SimpleNamespace(annotations=str(packets), out=str(output)))
    report = json.loads(output.read_text())
    assert report["n_annotators"] == 3 and report["n_items"] == 2
    assert set(report["slots"]) == set(annotation.RATING_SLOTS)
    assert all(result["fleiss_kappa"] == 1 for result in report["slots"].values())


def test_human_packets_reject_blank_field(tmp_path):
    packets = tmp_path / "packets"
    write_mock_packets(packets)
    path = packets / "annotator_1.csv"
    text = path.read_text().replace("MOCK_action", "", 1)
    path.write_text(text)
    with pytest.raises(SystemExit, match="Missing action"):
        annotation.load_completed_annotations(packets)


def test_balanced_three_family_matrix_passes():
    records = []
    for provider in ("openai", "anthropic", "gemini"):
        for item in ("mock-item-1", "mock-item-2"):
            for condition in ("direct", "situation"):
                records.append({"provider": provider, "model": f"{provider}-test",
                                "id": item, "condition": condition, "correct": 1,
                                "error": None, "usage": {}})
    report = multifamily.audit_records(records, ["direct", "situation"])
    assert report["n_families"] == 3 and report["n_cells_per_model"] == 4


def test_multifamily_rejects_mock_adapter():
    records = [{"provider": "mock", "model": "mock", "id": "x",
                "condition": "direct", "error": None, "usage": {"mock": True}}]
    with pytest.raises(ValueError, match="synthetic/mock"):
        multifamily.audit_records(records, ["direct"], min_families=1)
