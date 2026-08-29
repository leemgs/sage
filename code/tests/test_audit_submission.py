import importlib.util
from pathlib import Path


path = Path(__file__).parents[1] / "audit_submission.py"
spec = importlib.util.spec_from_file_location("audit_submission", path)
submission = importlib.util.module_from_spec(spec)
spec.loader.exec_module(submission)


def test_submission_package_passes_integrity_gate():
    report = submission.audit()
    assert report["status"] == "PASS", report["errors"]
    assert not report["errors"]
