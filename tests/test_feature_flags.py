import pytest
from roster.feature_flags import FeatureFlags
def test_feature_flags_default_and_snapshot():
    f=FeatureFlags({"voice":True}); assert f.enabled("voice"); assert not f.enabled("missing"); f.set("memory",True); assert f.snapshot()=={"voice":True,"memory":True}
def test_feature_flags_reject_empty_name():
    with pytest.raises(ValueError): FeatureFlags().set("  ",True)
