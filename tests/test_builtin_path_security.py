import pytest
from roster.tools.builtin import ToolExecutor

def test_safe_path_accepts_configured_root(monkeypatch,tmp_path):
    monkeypatch.setenv("ROSTER_ALLOWED_PATHS",str(tmp_path))
    assert ToolExecutor._safe_path(str(tmp_path/"file.txt")).parent==tmp_path.resolve()

def test_safe_path_rejects_outside_root(monkeypatch,tmp_path):
    allowed=tmp_path/"allowed"; allowed.mkdir()
    outside=tmp_path/"outside"; outside.mkdir()
    monkeypatch.setenv("ROSTER_ALLOWED_PATHS",str(allowed))
    with pytest.raises(PermissionError):
        ToolExecutor._safe_path(str(outside/"secret.txt"))
