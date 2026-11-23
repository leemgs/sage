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


def test_workbook_round_trip(tmp_path):
    from types import SimpleNamespace
    from openpyxl import load_workbook
    spec2 = importlib.util.spec_from_file_location("annotation_workbooks",
                                                   CODE / "annotation_workbooks.py")
    wbmod = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(wbmod)
    packets = CODE.parent / "paper" / "annotation_packets"
    wbmod.make(SimpleNamespace(packets=str(packets), out=str(tmp_path)))
    path = tmp_path / "annotator_2.xlsx"
    wb = load_workbook(path)
    ws = wb["Items"]
    header = [c.value for c in ws[1]]
    assert header[:5] == ["blind_id", "item_id", "question", "query_time", "evidence"]
    for row in ws.iter_rows(min_row=3):
        for c in row:
            h = header[c.column - 1]
            if h in cli.ALLOWED:
                c.value = cli.ALLOWED[h][0]
            elif h == "answer":
                c.value = " Yes "
    wb.save(path)
    out = tmp_path / "filled"
    out.mkdir()
    wbmod.to_csv(SimpleNamespace(packets=str(packets), xlsx=str(path), out=str(out / "annotator_2.csv")))
    rows = list(csv.DictReader((out / "annotator_2.csv").open(encoding="utf-8")))
    original = list(csv.DictReader((packets / "annotator_2.csv").open(encoding="utf-8")))
    assert [r["evidence"] for r in rows] == [r["evidence"] for r in original]
    assert {r["action"] for r in rows} == {"ANSWER"} and {r["answer"] for r in rows} == {"Yes"}


def test_declared_missing_cell_drops_item_from_that_slot_only(tmp_path):
    import json
    from types import SimpleNamespace
    write(tmp_path, [{}, {"answer": ""}, {}])
    with pytest.raises(SystemExit, match="Missing answer"):
        cli.load_completed_annotations(tmp_path)
    out = tmp_path / "agreement.json"
    cli.score(SimpleNamespace(annotations=str(tmp_path), out=str(out),
                              provenance="human_annotations", missing=["answer:x-1"]))
    report = json.loads(out.read_text())
    assert report["slots"]["answer"] == {"n_items": 0, "fleiss_kappa": None, "unanimous_rate": None}
    assert report["slots"]["world"]["n_items"] == 1
    assert report["declared_missing_cells_dropped"] == [{"slot": "answer", "item_id": "x-1"}]
