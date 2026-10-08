import pytest
from roster.tool_validation import ToolValidationError, validate_arguments

def test_validation_requires_declared_arguments():
    schema={"required":["query"],"properties":{"query":{"type":"string"}}}
    assert validate_arguments(schema,{"query":"hello"})["query"]=="hello"
    with pytest.raises(ToolValidationError): validate_arguments(schema,{})

def test_validation_rejects_unknown_arguments():
    with pytest.raises(ToolValidationError): validate_arguments({"properties":{"q":{}}},{"x":1})
