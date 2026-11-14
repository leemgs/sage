"""Tests for the E8 tooling, on synthetic records only (no study data)."""
import importlib.util
import io
import json
import sys
import urllib.error
from pathlib import Path

import pytest

CODE = Path(__file__).parents[1]
sys.path.insert(0, str(CODE))


def load(name):
    spec = importlib.util.spec_from_file_location(name, CODE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load("run_multimodel_eval")
nl = load("e8_nl_stats")


def http_error(code, body):
    return urllib.error.HTTPError("u", code, "x", {}, io.BytesIO(body.encode()))


def test_daily_quota_stops_without_retry(monkeypatch):
    calls = []

    def fake(*a, **k):
        calls.append(1)
        raise http_error(429, '{"error":{"message":"Rate limit exceeded: free-models-per-day-high-balance."}}')
    monkeypatch.setattr(runner.urllib.request, "urlopen", fake)
    with pytest.raises(runner.DailyQuotaExhausted):
        runner.post("https://example.invalid", {}, {})
    assert len(calls) == 1


def test_per_minute_429_is_still_retried(monkeypatch):
    calls = []

    def fake(*a, **k):
        calls.append(1)
        raise http_error(429, '{"error":{"message":"Rate limit exceeded: per-minute"}}')
    monkeypatch.setattr(runner.urllib.request, "urlopen", fake)
    monkeypatch.setattr(runner.time, "sleep", lambda s: None)
    with pytest.raises(RuntimeError):
        runner.post("https://example.invalid", {}, {}, max_retries=2)
    assert len(calls) == 3


def ids_and_records(correct):
    ids, recs = [], []
    for i, (dt, cl) in enumerate([("orig", "a"), ("start", "b"), ("start", "b"),
                                  ("sampled_year", "c")]):
        ids.append({"id": f"x{i}", "cluster": cl, "date_type": dt, "date": "2000"})
        for c in nl.CONDS:
            recs.append({"id": f"x{i}", "model": "m", "condition": c,
                         "correct": correct(dt, c), "error": None})
    return ids, recs


def test_nl_contrasts_on_synthetic_records():
    # undated direct fails only on time-dependent items; situation == structured
    ids, recs = ids_and_records(lambda dt, c: 0 if (c == "direct" and dt != "orig") else 1)
    s = nl.analyse(recs, ids)
    assert s["nl_h1_situation_minus_structured"]["estimate_pp"] == 0
    assert s["nl_h2_dated_minus_undated_time_dependent"]["estimate_pp"] == 100
    assert s["nl_h2_dated_minus_undated_static_control"]["estimate_pp"] == 0
    assert s["clusters"] == 3


def test_nl_stats_fail_closed_when_incomplete():
    ids, recs = ids_and_records(lambda dt, c: 1)
    recs[0]["error"] = "RuntimeError: HTTP 400"
    with pytest.raises(SystemExit):
        nl.analyse(recs, ids)


geo = load("e9_geo_stats")


def test_geo_contrasts_on_synthetic_records():
    ids = [{"id": f"g{i}", "cluster": c, "location": loc}
           for i, (c, loc) in enumerate([("a", "United States"), ("a", "India"), ("b", "Japan")])]
    recs = [{"id": r["id"], "model": "m", "condition": c,
             "correct": 0 if c == "direct" else 1, "error": None}
            for r in ids for c in geo.CONDS]
    s = geo.analyse(recs, ids)
    assert s["geo_h2_located_minus_unlocated"]["estimate_pp"] == 100
    assert s["geo_h1_situation_minus_structured"]["estimate_pp"] == 0
    assert s["descriptive_h2_us_located"]["n"] == 1 and s["clusters"] == 2


def test_location_context_uses_direct_prompt_and_raw_answer():
    assert runner.extract_answer("Paris", "location_context") == "Paris"
