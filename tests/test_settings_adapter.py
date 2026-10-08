from roster.advanced_settings import AdvancedSettings
from roster.settings_adapter import intelligence_limits

def test_settings_adapter_reads_typed_limits(tmp_path):
    result=intelligence_limits(AdvancedSettings(tmp_path/"settings.json")); assert result["memory_enabled"] is True; assert result["max_messages"]==24
