from roster.metrics import Metrics


def test_metrics_counts_and_snapshots():
    metrics = Metrics()
    assert metrics.increment("requests") == 1
    metrics.increment("requests", 2)
    metrics.observe("latency", 0.25)
    snapshot = metrics.snapshot()
    assert snapshot.counters["requests"] == 3
    assert snapshot.timings["latency"]["count"] == 1


def test_metrics_timer_records_duration():
    metrics = Metrics()
    with metrics.time("request"):
        pass
    assert metrics.snapshot().timings["request"]["count"] == 1


def test_metrics_reject_invalid_values():
    metrics = Metrics()
    for operation in (
        lambda: metrics.increment("x", -1),
        lambda: metrics.observe("x", -0.1),
        lambda: metrics.increment("", 1),
    ):
        try:
            operation()
        except ValueError:
            pass
        else:
            raise AssertionError("invalid metric value was accepted")
