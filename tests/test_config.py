import os

from roster.config import _env_float, _env_int


def test_env_float_falls_back_for_invalid_and_negative_values(monkeypatch):
    monkeypatch.setenv("ROSTER_TEST_FLOAT", "not-a-number")
    assert _env_float("ROSTER_TEST_FLOAT", 2.5, 0.1) == 2.5

    monkeypatch.setenv("ROSTER_TEST_FLOAT", "-1")
    assert _env_float("ROSTER_TEST_FLOAT", 2.5, 0.1) == 2.5

    monkeypatch.setenv("ROSTER_TEST_FLOAT", "1.75")
    assert _env_float("ROSTER_TEST_FLOAT", 2.5, 0.1) == 1.75


def test_env_int_falls_back_for_invalid_and_non_positive_values(monkeypatch):
    monkeypatch.setenv("ROSTER_TEST_INT", "broken")
    assert _env_int("ROSTER_TEST_INT", 4096, 1) == 4096

    monkeypatch.setenv("ROSTER_TEST_INT", "0")
    assert _env_int("ROSTER_TEST_INT", 4096, 1) == 4096

    monkeypatch.setenv("ROSTER_TEST_INT", "8192")
    assert _env_int("ROSTER_TEST_INT", 4096, 1) == 8192
