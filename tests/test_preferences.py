from roster.preferences import Preferences


def test_preferences_round_trip(tmp_path):
    preferences = Preferences(tmp_path / "preferences.json")
    assert preferences.get("theme") is None
    preferences.set("theme", "dark")
    preferences.set("voice_rate", 180)
    assert preferences.get("theme") == "dark"
    assert preferences.get("voice_rate") == 180


def test_preferences_recovers_from_corrupt_file(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text("{broken", encoding="utf-8")
    assert Preferences(path).load() == {}
