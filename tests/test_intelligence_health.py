from roster.advanced_settings import AdvancedSettings
from roster.intelligence_health import report

def test_intelligence_health_is_non_secret(tmp_path):
    result=report(object(),AdvancedSettings(tmp_path/"settings.json"))
    assert result["memory"] is True
    assert result["memory_enabled"] is True
