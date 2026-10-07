from roster.config import _env_float, _env_int


def test_invalid_numeric_environment_values_use_defaults(monkeypatch):
    monkeypatch.setenv("ROSTER_TEST_FLOAT", "bad")
    monkeypatch.setenv("ROSTER_TEST_INT", "bad")
    assert _env_float("ROSTER_TEST_FLOAT", 2.5, 0.1) == 2.5
    assert _env_int("ROSTER_TEST_INT", 4096, 1) == 4096


def test_numeric_environment_values_respect_bounds(monkeypatch):
    monkeypatch.setenv("ROSTER_TEST_FLOAT", "-1")
    monkeypatch.setenv("ROSTER_TEST_INT", "0")
    assert _env_float("ROSTER_TEST_FLOAT", 2.5, 0.1) == 2.5
    assert _env_int("ROSTER_TEST_INT", 4096, 1) == 4096
