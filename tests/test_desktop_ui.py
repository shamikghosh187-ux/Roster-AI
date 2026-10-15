import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication

from dataclasses import replace
from roster.config import settings
from roster.ui import app as desktop


@pytest.fixture(scope="session")
def qt_app():
    return QApplication.instance() or QApplication([])


def test_desktop_pages_and_busy_provider_selection(monkeypatch, tmp_path, qt_app):
    class DummyProvider:
        names = ("dummy",)

    monkeypatch.setattr(
        desktop,
        "settings",
        replace(settings, memory_db_path=str(tmp_path / "memory.sqlite3")),
    )
    monkeypatch.setattr(desktop, "create_router", lambda: DummyProvider())
    monkeypatch.setattr(desktop, "create_provider", lambda name: DummyProvider())

    window = desktop.MainWindow()
    try:
        assert set(window.pages) == {
            "Conversation", "Memory", "Tools", "Tasks", "Diagnostics",
        }
        assert window.provider_box.currentText() == "auto"

        window.provider_box.setCurrentText("gemini")
        assert window._selected_provider == "gemini"

        window.busy = True
        window.provider_box.setCurrentText("groq")
        assert window.provider_box.currentText() == "gemini"
        assert window._selected_provider == "gemini"
    finally:
        window.busy = False
        window.close()
