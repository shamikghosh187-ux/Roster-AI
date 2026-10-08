from roster.advanced_settings import AdvancedSettings
from roster.intelligence_health import report

def test_intelligence_health_is_non_secret(): assert report(object(),AdvancedSettings({"settings.json"}))["memory"] is True
