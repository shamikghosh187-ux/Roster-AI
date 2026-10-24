import subprocess
import sys


def test_desktop_ui_is_lazy_imported():
    # Run in a fresh interpreter so earlier Qt/UI tests cannot pollute
    # sys.modules and make this import-boundary check order-dependent.
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import main; "
            "assert 'roster.ui.app' not in sys.modules; "
            "assert callable(main.parse_args)",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_desktop_requirements_are_separate():
    from pathlib import Path

    text = Path("requirements-desktop.txt").read_text(encoding="utf-8")
    assert "PySide6" in text
