from roster.tool_enablement import ToolEnablement

def test_tools_can_be_disabled_and_enabled():
    state=ToolEnablement(); state.disable("Search")
    assert not state.is_enabled("search")
    state.enable("search")
    assert state.is_enabled("search")
