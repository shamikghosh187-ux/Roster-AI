import pytest
from roster.tool_contract import ToolContract

def test_tool_contract_requires_name():
    with pytest.raises(ValueError): ToolContract(name="",description="x")

def test_tool_contract_records_schema_and_sensitivity():
    tool=ToolContract("search","Search web",input_schema={"query":"string"},sensitive=True)
    assert tool.input_schema["query"]=="string"
    assert tool.sensitive is True
