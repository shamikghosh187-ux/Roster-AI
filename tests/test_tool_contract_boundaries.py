from roster.tool_contract import ToolContract

def test_tool_contract_isolates_input_schema():
    schema={"required":["query"]}
    contract=ToolContract("search","Search",input_schema=schema)
    schema["required"].append("extra")
    assert contract.input_schema["required"]==["query"]
