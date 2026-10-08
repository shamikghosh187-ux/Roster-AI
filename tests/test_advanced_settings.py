from roster.advanced_settings import AdvancedSettings, SettingsError


def test_defaults_and_typed_updates(tmp_path):
    settings = AdvancedSettings(tmp_path / "settings.json")
    assert settings.get("assistant.autonomy") == "balanced"
    settings.set("assistant.max_parallel_tasks", "4")
    settings.set("wake.sensitivity", "0.8")
    assert settings.get("assistant.max_parallel_tasks") == 4
    assert settings.get("wake.sensitivity") == 0.8


def test_atomic_persistence_and_reset(tmp_path):
    path = tmp_path / "settings.json"
    first = AdvancedSettings(path)
    first.set("privacy.mode", "strict")
    second = AdvancedSettings(path)
    assert second.get("privacy.mode") == "strict"
    second.reset("privacy.mode")
    assert AdvancedSettings(path).get("privacy.mode") == "standard"


def test_validation_rejects_bad_values(tmp_path):
    settings = AdvancedSettings(tmp_path / "settings.json")
    try:
        settings.set("wake.sensitivity", 2)
    except SettingsError as exc:
        assert "wake.sensitivity" in str(exc)
    else:
        raise AssertionError("invalid value was accepted")


def test_callbacks_receive_changes(tmp_path):
    settings = AdvancedSettings(tmp_path / "settings.json")
    changes = []
    settings.on_change(lambda key, old, new: changes.append((key, old, new)))
    settings.set("voice.interruptible", False)
    assert changes == [("voice.interruptible", True, False)]


def test_profile_is_path_safe(tmp_path):
    settings = AdvancedSettings(tmp_path / "settings.json")
    settings.set_profile("focus")
    assert settings.profile() == "focus"
    try:
        settings.set_profile("../escape")
    except SettingsError:
        pass
    else:
        raise AssertionError("unsafe profile name was accepted")
