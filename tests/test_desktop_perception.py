import json

import pytest

from roster.desktop_perception import DesktopPerception, DesktopPerceptionError, _extract_json


class FakePyAutoGUI:
    def size(self):
        return (1920, 1080)

    def screenshot(self, path):
        with open(path, "wb") as handle:
            handle.write(b"fake-png")


class FakeProvider:
    def vision(self, prompt, image):
        assert "Return ONLY valid JSON" in prompt
        assert image.startswith("data:image/png;base64,")
        return json.dumps(
            {
                "active_window_id": "w1",
                "confidence": 0.91,
                "windows": [
                    {
                        "id": "w1",
                        "title": "Editor",
                        "app": "Code",
                        "focused": True,
                        "confidence": 0.94,
                        "bounds": [0, 0, 1000, 800],
                        "elements": [
                            {
                                "id": "e1",
                                "role": "button",
                                "label": "Run",
                                "bounds": [20, 30, 80, 30],
                                "confidence": 0.88,
                            }
                        ],
                    }
                ],
            }
        )


def test_extract_json_rejects_non_object():
    with pytest.raises(DesktopPerceptionError):
        _extract_json("[]")


def test_capture_normalizes_vision_output(monkeypatch):
    import sys
    import types

    fake = FakePyAutoGUI()
    fake_module = types.SimpleNamespace(size=fake.size, screenshot=fake.screenshot)
    monkeypatch.setitem(sys.modules, "pyautogui", fake_module)

    state = DesktopPerception(FakeProvider()).capture(reason="test")
    assert state.source == "vision"
    assert state.screen_size == (1920, 1080)
    assert state.active_window_id == "w1"
    assert state.windows[0].focused is True
    assert state.windows[0].elements[0].element_id == "e1"
    assert state.windows[0].elements[0].label == "Run"
    assert state.windows[0].elements[0].bounds == (20, 30, 80, 30)


def test_capture_without_provider_is_observation_only(monkeypatch):
    import sys
    import types

    fake = FakePyAutoGUI()
    fake_module = types.SimpleNamespace(size=fake.size, screenshot=fake.screenshot)
    monkeypatch.setitem(sys.modules, "pyautogui", fake_module)

    state = DesktopPerception().capture()
    assert state.source == "local"
    assert state.windows == ()
    assert state.confidence == 0.25
