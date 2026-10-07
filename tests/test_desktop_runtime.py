def test_desktop_ui_is_lazy_imported():
    import sys
    import main
    assert "roster.ui.app" not in sys.modules
    assert callable(main.parse_args)

def test_desktop_requirements_are_separate():
    from pathlib import Path
    text = Path("requirements-desktop.txt").read_text(encoding="utf-8")
    assert "PySide6" in text
