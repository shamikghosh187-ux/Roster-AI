import pytest

from roster.tools.builtin import ToolExecutor


def test_builtin_file_paths_are_scoped_by_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert ToolExecutor()._safe_path("inside.txt") == (tmp_path / "inside.txt").resolve()
    with pytest.raises(PermissionError):
        ToolExecutor()._safe_path(str(tmp_path.parent / "outside.txt"))


def test_builtin_file_paths_allow_explicit_extra_root(tmp_path, monkeypatch):
    project = tmp_path / "project"
    extra = tmp_path / "documents"
    project.mkdir()
    extra.mkdir()
    monkeypatch.chdir(project)
    monkeypatch.setenv("ROSTER_ALLOWED_PATHS", str(extra))
    assert ToolExecutor()._safe_path(extra / "note.txt") == (extra / "note.txt").resolve()
