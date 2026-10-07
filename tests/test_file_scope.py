import os

import pytest

from roster.tools.builtin import ToolExecutor


def test_builtin_file_paths_are_scoped_by_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    inside = ToolExecutor()._safe_path("inside.txt")
    assert inside == (tmp_path / "inside.txt").resolve()

    outside = tmp_path.parent / "outside.txt"
    with pytest.raises(PermissionError):
        ToolExecutor()._safe_path(str(outside))


def test_builtin_file_paths_can_use_explicit_extra_root(tmp_path, monkeypatch):
    project = tmp_path / "project"
    extra = tmp_path / "documents"
    project.mkdir()
    extra.mkdir()
    monkeypatch.chdir(project)
    monkeypatch.setenv("ROSTER_ALLOWED_PATHS", str(extra))
    assert ToolExecutor()._safe_path(extra / "note.txt") == (extra / "note.txt").resolve()
