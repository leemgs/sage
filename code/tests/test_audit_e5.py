import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "audit_e5.py"
SPEC = importlib.util.spec_from_file_location("audit_e5", MODULE_PATH)
audit_e5 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_e5)


def test_choose_records_prefers_latest_success_over_later_error():
    records = [
        {"id": "x", "condition": "direct", "correct": 1,
         "completed_at": "2026-01-01T00:00:00Z"},
        {"id": "x", "condition": "direct", "correct": None,
         "completed_at": "2026-01-02T00:00:00Z"},
        {"id": "x", "condition": "direct", "correct": 0,
         "completed_at": "2026-01-01T12:00:00Z"},
    ]
    chosen, duplicates = audit_e5.choose_records(records)
    assert duplicates == 2
    assert chosen[("x", "direct")]["correct"] == 0


def test_token_total_normalizes_provider_schemas():
    assert audit_e5.token_total({"totalTokenCount": 12}) == 12
    assert audit_e5.token_total({"prompt_tokens": 7,
                                 "completion_tokens": 5}) == 12
    assert audit_e5.token_total({"input_tokens": 9, "output_tokens": 3}) == 12
