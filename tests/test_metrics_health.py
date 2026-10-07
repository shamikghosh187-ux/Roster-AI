from roster.health import collect_health
from roster.metrics import RuntimeMetrics


def test_metrics_track_lifecycle():
    metrics = RuntimeMetrics()
    metrics.started()
    metrics.finished("completed")
    metrics.started()
    metrics.finished("failed")
    metrics.started()
    metrics.finished("cancelled")
    snapshot = metrics.snapshot()
    assert snapshot.submitted == 3
    assert snapshot.completed == 1
    assert snapshot.failed == 1
    assert snapshot.cancelled == 1
    assert snapshot.active is False
    assert snapshot.last_duration_ms is not None


def test_health_report_has_expected_shape():
    report = collect_health()
    assert "ok" in report
    assert "checks" in report
    assert report["checks"]
    assert all({"name", "ok", "detail"} <= set(item) for item in report["checks"])
