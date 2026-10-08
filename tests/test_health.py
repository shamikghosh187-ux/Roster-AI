from roster.health import HealthCheck, HealthRegistry


def test_health_registry_reports_ready():
    registry = HealthRegistry()
    registry.register("database", lambda: HealthCheck("database", True, "ok"))
    report = registry.run()
    assert report.ready
    assert report.as_dict()["checks"][0]["name"] == "database"


def test_health_registry_contains_failures():
    registry = HealthRegistry()
    registry.register("broken", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    report = registry.run()
    assert report.status == "degraded"
    assert report.checks[0].detail == "RuntimeError"


def test_health_registry_rejects_duplicate_names():
    registry = HealthRegistry()
    registry.register("x", lambda: HealthCheck("x", True))
    try:
        registry.register("x", lambda: HealthCheck("x", True))
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate health check was accepted")
