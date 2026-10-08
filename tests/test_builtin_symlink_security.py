from roster.models import Action,Intent
from roster.tools.builtin import ToolExecutor

def test_find_in_files_does_not_follow_symlink_outside_allowed_root(tmp_path,monkeypatch):
    allowed=tmp_path/"allowed"
    outside=tmp_path/"outside"
    allowed.mkdir()
    outside.mkdir()
    (outside/"secret.txt").write_text("needle",encoding="utf-8")
    (allowed/"link.txt").symlink_to(outside/"secret.txt")

    monkeypatch.setenv("ROSTER_ALLOWED_PATHS",str(allowed))
    tool=ToolExecutor()
    intent=Intent(Action.FIND_IN_FILES,f"{allowed}::needle")
    result=tool._find_in_files(intent,"",None)

    assert result=="No matches found."
