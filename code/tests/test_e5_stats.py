import importlib.util
from pathlib import Path


path = Path(__file__).parents[1] / "e5_stats.py"
spec = importlib.util.spec_from_file_location("e5_stats", path)
stats = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stats)


def test_cluster_bootstrap_is_order_and_call_independent():
    forward = {"b": [0, 1, 1], "a": [1, 1, 1]}
    reverse = {"a": [1, 1, 1], "b": [0, 1, 1]}
    first = stats.cluster_bootstrap(forward, stats.mean, 200)
    stats.cluster_bootstrap({"unrelated": [0, 0, 1]}, stats.mean, 200)
    assert stats.cluster_bootstrap(reverse, stats.mean, 200) == first
